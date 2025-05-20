from fastapi import APIRouter, Query
from services.task_services import create_new_task

router = APIRouter()

@router.post("/tasks/create")
def create_task(task_name: str = Query(..., min_length=1)):
    return {"message": create_new_task(task_name)}
