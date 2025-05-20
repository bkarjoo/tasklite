from fastapi import APIRouter, Query
from services.task_services import (
    create_new_task,
    get_task_roots_list,
    get_task_roots_list_all
)
from typing import Optional

router = APIRouter()

@router.post("/tasks/create")
def create_task(task_name: str = Query(..., min_length=1)):
    return {"message": create_new_task(task_name)}


@router.get("/tasks/trl")
def trl(message: Optional[str] = Query(None)):
    return {"tasks": get_task_roots_list(message)}


@router.get("/tasks/tl")
def tl(message: Optional[str] = Query(None)):
    return {"tasks": get_task_roots_list(message)}


@router.get("/tasks/tla")
def tla(message: Optional[str] = Query(None)):
    return {"tasks": get_task_roots_list_all(message)}