from data.models.tag_model import TaskTag
from data.models.task_model import Task
from sqlalchemy import func, select
from sqlalchemy.orm import Session


def add_tag_to_task(session: Session, task: Task, tag_name: str):
    tag = session.query(TaskTag).filter_by(name=tag_name).first()
    if not tag:
        tag = TaskTag(name=tag_name)
        session.add(tag)
        session.flush()  # Assign ID without commit

    if tag not in task.tasktags:
        task.tasktags.append(tag)

def remove_tag_from_task(session: Session, task: Task, tag_name: str):
    tag = session.query(TaskTag).filter_by(name=tag_name).first()
    if tag and tag in task.tasktags:
        task.tasktags.remove(tag)

def get_tags_for_task(session: Session, task: Task) -> list[str]:
    return [tag.name for tag in task.tasktags]


def get_tasks_by_tag_name(session: Session, tag_name: str):
    return (
        session.query(Task)
        .join(Task.tasktags)
        .filter(
            TaskTag.name == tag_name,
            Task.status != "Completed",
            Task.deleted == False
        )
        .all()
    )


def count_tasks_by_tag(session: Session, tag_name: str) -> int:
    """
    Returns the number of tasks that have the given tag,
    excluding tasks that are deleted or marked as completed.
    """
    query = (
        select(func.count(Task.taskid))
        .join(Task.tasktags)
        .where(
            TaskTag.name == tag_name,
            Task.deleted.is_(False),
            Task.status != 'Completed'
        )
    )
    count = session.execute(query).scalar()
    return count or 0