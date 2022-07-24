from datetime import datetime
from pydantic import BaseModel


class Task(BaseModel):
    id: str
    schedule: str
    next_run_time: datetime