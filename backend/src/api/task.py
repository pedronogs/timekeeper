import io
import tarfile
import uuid

from datetime import datetime
from typing import List

import docker
from apscheduler.triggers.cron import CronTrigger
from backend.src.dependencies.containers import Container
from backend.src.models.task import TaskRequest, TaskResponse
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from loguru import logger

router = APIRouter()

global docker_client
docker_client = docker.from_env()
docker_client.volumes.create("timekeeper-client-scripts")


def get_cron_from_trigger(trigger: CronTrigger) -> str:
    cron_fields = trigger.fields

    cron_string = [""] * 5
    cron_pattern = ["minute", "hour", "day", "month", "day_of_week"]
    for f in cron_fields:
        if f.name in cron_pattern:
            idx = cron_pattern.index(f.name)
            cron_string[idx] = str(f)

    return " ".join(cron_string)


@router.get("/api/tasks")
@inject
def get_tasks(scheduler=Depends(Provide[Container.scheduler])) -> List[TaskResponse]:
    tasks: List[TaskResponse] = []
    for job in scheduler().get_jobs():
        tasks.append(
            TaskResponse(
                id=job.id,
                name=job.name,
                trigger=get_cron_from_trigger(job.trigger),
                last_run_time=None,
                next_run_time=job.next_run_time
            )
        )

    return tasks


@router.put("/api/tasks/{task_id}/pause")
@inject
def pause_task(task_id: str, scheduler=Depends(Provide[Container.scheduler])):
    job = scheduler().get_job(task_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    job.pause()
    job = scheduler().get_job(task_id)  # This is necessary because pause does not return updated job metadata

    return TaskResponse(
        id=task_id,
        name=job.name,
        trigger=get_cron_from_trigger(job.trigger),
        last_run_time=None,
        next_run_time=job.next_run_time
    )


@router.put("/api/tasks/{task_id}/resume")
@inject
def resume_task(task_id: str, scheduler=Depends(Provide[Container.scheduler])):
    job = scheduler().get_job(task_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    job.resume()
    job = scheduler().get_job(task_id)  # This is necessary because pause does not return updated job metadata

    return TaskResponse(
        id=task_id,
        name=job.name,
        trigger=get_cron_from_trigger(job.trigger),
        last_run_time=None,
        next_run_time=job.next_run_time
    )


@router.put("/api/tasks/{task_id}/start")
@inject
def start_task(task_id: str, scheduler=Depends(Provide[Container.scheduler])):
    job = scheduler().get_job(task_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    job.modify(next_run_time=datetime.now())
    job = scheduler().get_job(task_id)  # This is necessary because pause does not return updated job metadata

    return TaskResponse(
        id=task_id,
        name=job.name,
        trigger=get_cron_from_trigger(job.trigger),
        last_run_time=None,
        next_run_time=job.next_run_time
    )


@router.put("/api/tasks/{task_id}")
@inject
def update_task(task_id: str, task_request: TaskRequest, scheduler=Depends(Provide[Container.scheduler])):
    job = scheduler().get_job(task_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    try:
        trigger_cron = CronTrigger.from_crontab(task_request.trigger)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid cron expression.")

    job.modify(name=task_request.name)
    job.reschedule(trigger_cron)
    job = scheduler().get_job(
        task_id
    )  # This is necessary because modify and reschedule does not return updated job metadata

    return TaskResponse(
        id=task_id,
        name=job.name,
        trigger=get_cron_from_trigger(job.trigger),
        last_run_time=None,
        next_run_time=job.next_run_time
    )


@router.delete("/api/tasks/{task_id}", status_code=204)
@inject
def delete_task(task_id: str, scheduler=Depends(Provide[Container.scheduler])) -> None:
    job = scheduler().get_job(task_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    job.remove()


async def run_job(filename: str = None):
    container = docker_client.containers.run(
        "python:3.8.13-alpine",
        f"python /opt/timekeeper/{filename}",
        volumes={"timekeeper-client-scripts": {
            "bind": "/opt/timekeeper",
            "mode": "ro"
        }},
        detach=True
    )

    result = container.wait()
    container.remove()

    return result


# Copy client script to "timekeeper-client-scripts" docker volume, available from main container
def copy_script_to_container(container: Container, script_content: bytes, script_name: str = None):
    src_stream = io.BytesIO(script_content)
    dst_stream = io.BytesIO()
    with tarfile.open(fileobj=dst_stream, mode='w|') as tar:
        info = tarfile.TarInfo(name=script_name)
        info.size = src_stream.getbuffer().nbytes
        tar.addfile(info, src_stream)
    dst_stream.seek(0)

    container.put_archive("/opt/timekeeper", dst_stream)


@router.post("/api/tasks", status_code=201)
@inject
async def create_task(
    name: str = Form(...),
    trigger: str = Form(...),
    file: UploadFile = File(...),
    mongo_client=Depends(Provide[Container.mongo_client]),
    scheduler=Depends(Provide[Container.scheduler])
) -> TaskResponse:
    task_data = TaskRequest(name=name, trigger=trigger)

    original_filename = file.filename
    file_ext = original_filename.split(".")[-1]
    if file.content_type != "text/x-python" or file_ext != "py":
        raise HTTPException(status_code=400, detail="Invalid file type.")

    content = await file.read()

    rname = str(uuid.uuid4()) + ".py"
    main_container = docker_client.containers.get("aae704e0d6748dd9f09cb558ec01f43af8f4e68f17c2cf892ab2d02c2345ce4f")
    copy_script_to_container(container=main_container, script_content=content, script_name=rname)

    try:
        trigger_cron = CronTrigger.from_crontab(trigger)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid cron expression.")

    job = scheduler().add_job(run_job, trigger_cron, kwargs={"filename": rname})

    try:
        mongo_client()["timekeeper"]["tasks"].insert_one(
            {
                "id": job.id,
                "name": task_data.name,
                "trigger": task_data.trigger,
                "original_filename": original_filename,
                "generated_filename": rname,
                "content": content
            }
        )
    except Exception as err:
        logger.error("Could not insert this task's data in MongoDB. Details: {}", err)
        scheduler().remove_job(job.id)

        raise HTTPException(status_code=500, detail="Error creating task.")

    return TaskResponse(
        id=job.id, name=task_data.name, trigger=task_data.trigger, last_run_time=None, next_run_time=job.next_run_time
    )
