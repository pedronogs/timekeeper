from fastapi import FastAPI, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uuid
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import List, Type

from backend.src.models.Task import Task

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
    global scheduler
    scheduler = AsyncIOScheduler()
    scheduler.start()


@app.get("/api/tasks")
async def get_tasks() -> List[Task]:
    tasks: List[Task] = []
    for job in scheduler.get_jobs():
        tasks.append(
            Task(id=job.id,
                 schedule=str(job.trigger),
                 next_run_time=job.next_run_time))

    return tasks


@app.post("/api/tasks")
async def create_task(file: UploadFile):
    content = await file.read()

    rname = str(uuid.uuid4())
    with open(f"backend/tasks/{rname}.py", "wb") as f:
        f.write(content)

    task = lambda: exec(content)
    scheduler.add_job(task, 'interval', seconds=10)

    return {"message": "Task created succesfully."}


app.mount("/",
          StaticFiles(directory="./frontend/dist", html=True),
          name="static")