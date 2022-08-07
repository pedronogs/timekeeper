from typing import List, Type

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.src.dependencies.containers import Container
from backend.src.api.task import router as task_router

app = FastAPI()

container = Container()

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.container = container
app.include_router(task_router)

app.mount("/", StaticFiles(directory="./frontend/dist", html=True), name="static")


@app.on_event("startup")
def startup():
    app.container.scheduler().start_scheduler()
