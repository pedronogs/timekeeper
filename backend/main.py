import asyncio
import sys

import docker
import zmq
from dependency_injector.wiring import Provide, inject
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from backend.src.api.task import router as task_router
from backend.src.dependencies.containers import Container

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

app.container = container  # type: ignore
app.include_router(task_router)

app.mount("/", StaticFiles(directory="./frontend/dist", html=True), name="static")


@app.on_event("startup")
def startup():
    app.container.scheduler().start_scheduler()

    app.container.docker_client()

    logger.configure(handlers=[{"sink": sys.stderr, "format": "{message}"}])
