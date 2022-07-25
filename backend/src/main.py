import uuid
from http.client import HTTPException
from typing import List, Type

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.src.models.Task import TaskRequest, TaskResponse
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
    scheduler.start()


@app.get("/api/tasks")
async def get_tasks() -> List[TaskResponse]:
    tasks: List[TaskResponse] = []
    for job in scheduler.get_jobs():
        tasks.append(
            TaskResponse(id=job.id,
                         name=job.name,
                         trigger=str(job.trigger),
                         last_run_time=None,
                         next_run_time=job.next_run_time))

    return tasks


@app.post("/api/tasks")
async def create_task(name: str = Form(...),
                      trigger: str = Form(...),
                      file: UploadFile = File(...)) -> TaskResponse:
    task_data = TaskRequest(name=name, trigger=trigger)

    file_ext = file.filename.split(".")[-1]
    print(file.content_type, file_ext)
    if file.content_type != "text/x-python" or file_ext != "py":
        raise HTTPException(status_code=400, detail="Invalid file type.")

    content = await file.read()

    rname = str(uuid.uuid4())
    fpath = f"backend/tasks/{rname}.py"
    with open(fpath, "wb") as f:
        f.write(content)

    task = lambda: exec(content)
    job = scheduler.add_job(task, 'interval', seconds=10)

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
