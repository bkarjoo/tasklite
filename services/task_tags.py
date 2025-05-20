from data.crud.task_crud import get_task_by_id as db_get_task_by_id
from data.crud.task_tags_crud import add_tag_to_task as db_add_tag
from data.crud.task_tags_crud import \
    count_tasks_by_tag  # assuming you defined this in the CRUD layer
from data.crud.task_tags_crud import get_tags_for_task as db_get_tags
from data.crud.task_tags_crud import \
    get_tasks_by_tag_name as db_get_tasks_by_tag_name
from data.crud.task_tags_crud import remove_tag_from_task as db_remove_tag
from data.db_session import SessionLocal


def add_tag(task_id: int, tag_name: str):
    with SessionLocal() as session:
        task = db_get_task_by_id(session, task_id)
        if task:
            db_add_tag(session, task, tag_name)
            session.commit()

def remove_tag(task_id: int, tag_name: str):
    with SessionLocal() as session:
        task = db_get_task_by_id(session, task_id)
        if task:
            db_remove_tag(session, task, tag_name)
            session.commit()

def list_tags(task_id: int) -> list[str]:
    with SessionLocal() as session:
        task = db_get_task_by_id(session, task_id)
        return db_get_tags(session, task) if task else []


def get_tasks_by_tag(tag_name: str) -> list:
    with SessionLocal() as session:
        return db_get_tasks_by_tag_name(session, tag_name)


def count_tasks_by_tag_service(tag_name: str) -> int:
    with SessionLocal() as session:
        return count_tasks_by_tag(session, tag_name)
