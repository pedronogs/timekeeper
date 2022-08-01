from fastapi import APIRouter
from typing import Optional
from apscheduler.triggers.cron import CronTrigger
from backend.src.models.task import TaskRequest, TaskResponse
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Depends
from http.client import HTTPException
from typing import List, Type
import uuid
from dependency_injector.wiring import inject, Provide
from backend.src.dependencies.containers import Container

router = APIRouter()

global scheduler
global mongo_client


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


def run_job(content: bytes = None):
    exec(content)


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

    file_ext = file.filename.split(".")[-1]
    if file.content_type != "text/x-python" or file_ext != "py":
        raise HTTPException(status_code=400, detail="Invalid file type.")

    content = await file.read()

    rname = str(uuid.uuid4())
    fpath = f"backend/tasks/{rname}.py"
    with open(fpath, "wb") as f:
        f.write(content)

    try:
        trigger_cron = CronTrigger.from_crontab(trigger)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid cron expression.")

    job = scheduler().add_job(run_job, trigger_cron, kwargs={"content": content})

    mongo_client()["timekeeper"]["tasks"].insert_one(
        {
            "id": job.id,
            "name": task_data.name,
            "trigger": task_data.trigger,
            "filepath": fpath
        }
    )

    return TaskResponse(
        id=job.id, name=task_data.name, trigger=task_data.trigger, last_run_time=None, next_run_time=job.next_run_time
    )
