import uuid
from http.client import HTTPException
from typing import List, Type

from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.src.models.task import TaskRequest, TaskResponse
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient

app = FastAPI()
scheduler = None

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('startup')
def init_data():
    global mongo_client
    mongo_client = MongoClient("mongodb://localhost:27017/")

    global scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_jobstore(
        MongoDBJobStore(client=mongo_client,
                        database="timekeeper",
                        collection="jobs"))
    scheduler.start()


def get_cron_from_trigger(trigger: CronTrigger) -> str:
    cron_fields = trigger.fields

    cron_string = [""] * 5
    cron_pattern = ["minute", "hour", "day", "month", "day_of_week"]
    for f in cron_fields:
        if f.name in cron_pattern:
            idx = cron_pattern.index(f.name)
            cron_string[idx] = str(f)

    return " ".join(cron_string)


@app.get("/api/tasks")
async def get_tasks() -> List[TaskResponse]:
    tasks: List[TaskResponse] = []
    for job in scheduler.get_jobs():
        tasks.append(
            TaskResponse(id=job.id,
                         name=job.name,
                         trigger=get_cron_from_trigger(job.trigger),
                         last_run_time=None,
                         next_run_time=job.next_run_time))

    return tasks


@app.put("/api/tasks/{task_id}")
def update_task(task_id: str, task_request: TaskRequest):
    job = scheduler.get_job(task_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    try:
        trigger_cron = CronTrigger.from_crontab(task_request.trigger)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid cron expression.")

    job.modify(name=task_request.name, trigger=trigger_cron)
    return TaskResponse(id=task_id,
                        name=job.name,
                        trigger=get_cron_from_trigger(job.trigger),
                        last_run_time=None,
                        next_run_time=job.next_run_time)


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: str) -> None:
    job = scheduler.get_job(task_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    job.remove()


def run_job(content: bytes = None):
    exec(content)


@app.post("/api/tasks", status_code=201)
async def create_task(name: str = Form(...),
                      trigger: str = Form(...),
                      file: UploadFile = File(...)) -> TaskResponse:
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

    job = scheduler.add_job(run_job, trigger_cron, kwargs={"content": content})

    mongo_client["timekeeper"]["tasks"].insert_one({
        "id": job.id,
        "name": task_data.name,
        "trigger": task_data.trigger,
        "filepath": fpath
    })

    return TaskResponse(id=job.id,
                        name=task_data.name,
                        trigger=task_data.trigger,
                        last_run_time=None,
                        next_run_time=job.next_run_time)


app.mount("/",
          StaticFiles(directory="./frontend/dist", html=True),
          name="static")
