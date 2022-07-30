from datetime import datetime
from pydantic import BaseModel


class TaskRequest(BaseModel):
    name: str
    trigger: str


class TaskResponse(BaseModel):
    id: str
    name: str
    trigger: str
    last_run_time: datetime = None
    next_run_time: datetime = None