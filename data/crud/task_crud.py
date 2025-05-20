import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from data.models.task_model import Task
from sqlalchemy import and_, exists, func, or_, select, update
from sqlalchemy.orm import Session, aliased


def get_root_tasks(session):
    query = (
        select(Task)
        .where(
            Task.status != "Completed",
            Task.deleted.is_(False),
            (Task.earlieststarttime.is_(None) | (Task.earlieststarttime <= datetime.now())),
            Task.parenttaskid == None
        )
        .order_by(Task.sort_order.asc())
    )
    tasks = session.execute(query).scalars().all()
    return tasks


def root_task_search(session, search_pattern):
    query = (
        select(Task)
        .where(
            Task.status != "Completed",
            Task.deleted.is_(False),
            (Task.earlieststarttime.is_(None) | (Task.earlieststarttime <= datetime.now())),
            Task.parenttaskid == None,
            Task.taskname.like(search_pattern)
        )
        .order_by(Task.sort_order.asc())
    )
    tasks = session.execute(query).scalars().all()
    return tasks


def get_root_tasks_all(session):
    query = (
        select(Task)
        .where(
            Task.status != "Completed",
            Task.deleted.is_(False),
            Task.parenttaskid == None
        )
        .order_by(Task.earlieststarttime.desc())
    )
    tasks = session.execute(query).scalars().all()
    return tasks

def get_stand_alone_available_tasks(session) -> list[int]:
    sub_task = aliased(Task)
    query = (
        select(Task.taskid)
        .where(
            Task.status != "Completed",
            Task.deleted.is_(False),
            (Task.earlieststarttime.is_(None) | (Task.earlieststarttime <= datetime.now())),
            ~exists().where(
                and_(
                    sub_task.parenttaskid == Task.taskid,
                    sub_task.status != "Completed"
                )
            )
        )
        .order_by(Task.sort_order.asc())
    )
    tasks = session.execute(query).scalars().all()
    return tasks

def get_all_available_incomplete_tasks(session) -> list[int]:
    root_tasks = get_stand_alone_available_tasks(session)
    all_tasks = []
    for task_id in root_tasks:
        all_tasks.extend(get_subtasks_tree(session, task_id))
    return list(set(all_tasks))

def get_all_available_incomplete_tasks_by_tag(session, tag_name: str):
    from data.models.tag_model import TaskTag
    child_task = aliased(Task)
    tasks = (
        session.query(Task.taskid)
        .join(Task.tasktags)
        .filter(
            TaskTag.name == tag_name,
            Task.status != "Completed",
            Task.deleted.is_(False),
            (Task.earlieststarttime.is_(None) | (Task.earlieststarttime <= datetime.now())),
            ~exists().where(
                and_(
                    child_task.parenttaskid == Task.taskid,
                    child_task.status != "Completed"
                )
            )
        )
        .distinct()
        .order_by(Task.sort_order.asc())
        .all()
    )
    return [task[0] for task in tasks]

def get_future_tasks(session):
    return (
        session.query(Task)
        .filter(
            Task.earlieststarttime > datetime.now(),
            Task.status != "Completed",
            Task.deleted == False
        )
        .order_by(Task.earlieststarttime.desc())
        .all()
    )


def create_task(session: Session, task_name: str) -> Optional[int]:
    try:
        new_task = Task(
            taskname=task_name,
            earlieststarttime=datetime.now(),
            status="Pending"  # Set a default status
        )
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        return new_task.taskid
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to create task '{task_name}': {e}")
        return None

def create_new_subtask(session: Session, parent_task_id: int, task_name: str) -> Optional[int]:
    try:
        new_subtask = Task(
            taskname=task_name,
            parenttaskid=parent_task_id,
            earlieststarttime=datetime.now(),
            status="Pending"  # Set a default status
        )
        session.add(new_subtask)
        session.commit()
        session.refresh(new_subtask)
        return new_subtask.taskid
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to create subtask '{task_name}' under parent task {parent_task_id}: {e}")
        return None




def id_exists(session: Session, id: int) -> bool:
    query = select(Task.taskid).where(Task.taskid == id)
    return session.execute(query).scalar() is not None


def find_root_task_id(session: Session, task_id: int) -> int:
    while True:
        task = session.get(Task, task_id)
        # Stop if the task is deleted, not found, or has no parent.
        if not task or task.deleted or task.parenttaskid is None:
            return task_id
        task_id = task.parenttaskid



def get_incomplete_available_important_tasks_ids(session: Session, task_ids: list[int]):

    query = (
        select(Task.taskid)
        .where(
            Task.taskid.in_(task_ids),
            Task.status != "Completed",
            Task.important.is_(True),
            Task.deleted.is_(False)
        )
    )

    important_tasks = session.execute(query).scalars().all()

    return important_tasks


def get_incomplete_available_urgent_tasks_ids(session: Session, task_ids: list[int]):

    query = (
        select(Task.taskid)
        .where(
            Task.taskid.in_(task_ids),
            Task.status != "Completed",
            Task.urgent.is_(True),
            Task.deleted.is_(False)
        )
    )

    urgent_tasks = session.execute(query).scalars().all()

    return urgent_tasks


def get_subtasks_all_ids(session: Session, task_id: int):
    query = (
        select(Task.taskid)
        .where(
            Task.parenttaskid == task_id,
            Task.deleted.is_(False)
        )
    )
    return session.execute(query).scalars().all()

def get_subtasks_all(session: Session, task_id: int):
    query = (
        select(Task)
        .where(
            Task.parenttaskid == task_id,
            Task.deleted.is_(False)
        )
    )
    return session.execute(query).scalars().all()


def get_subtask_ids_all(session: Session, task_id: int):
    query = (
        select(Task.taskid)
        .where(
            Task.parenttaskid == task_id,
            Task.status != "Completed",
            Task.deleted.is_(False)
        )
    )
    result = session.execute(query).scalars().all()
    return result


def format_task_tree_new(
    session: Session,
    selected_id: int,
    task_id: int,
    start_index: int,
    ordered_task_list: Dict[int, Dict[str, int | str]],
    indent_level: int = 0,
    is_last: bool = False
) -> Tuple[str, int]:

    if not task_id:
        return "", start_index


    task = session.get(Task, task_id)
    task_name = task.taskname if task else "Unknown Task"

    ordered_task_list[start_index] = {'id': task_id, 'name': task_name}


    indent = ".   " * indent_level
    branch = "└── " if is_last else "├── "

    bold = "**" if task_id == selected_id else ""

    if indent_level == 0:
        task_line = f"{indent}{branch}[Task] {bold}{task_name} ({task_id}){bold}\n"
    else:
        task_line = f"{indent}{branch}[Subtask] {bold}{task_name} ({task_id}){bold}\n"

    subtasks = get_subtask_ids_all(session, task_id)

    for subtask_index, subtask_id in enumerate(subtasks):
        subtask_is_last = subtask_index == len(subtasks) - 1
        subtask_extension, new_index = format_task_tree_new(session, selected_id, subtask_id, start_index + 1, ordered_task_list, indent_level + 1, subtask_is_last)
        task_line += subtask_extension
        start_index = new_index

    return task_line, start_index


def task_read_subtasks(session: Session, selected_id: int, task_id: int) -> Tuple[str, Dict[int, Dict[str, int | str]]]:

    tree_view = ""
    ordered_task_list = {}
    global_task_index = 1

    task_tree_formatted = format_task_tree_new(session, selected_id, task_id, global_task_index, ordered_task_list,
                                               indent_level=0, is_last=True)

    if not task_tree_formatted:
        return "", {}

    tree_extension, new_index = task_tree_formatted
    tree_view += tree_extension
    global_task_index = new_index

    tree_view += "\n"
    return tree_view, ordered_task_list


def has_incomplete_subtask(session: Session, task_id: int) -> bool:

    subquery = (
        select(exists().where(Task.parenttaskid == task_id, Task.status != "Completed"))
    )
    return session.execute(subquery).scalar()


def get_subtasks(session: Session, task_id: int):

    # Subquery to find the minimum sequence of incomplete subtasks for the given parent
    min_sequence_subquery = (
        select(func.min(Task.repeatinterval))  # Assuming Sequence is repeatinterval
        .where(Task.parenttaskid == task_id, Task.status != "Completed")
    ).scalar_subquery()

    query = (
        select(Task.taskid)
        .where(
            Task.parenttaskid == task_id,
            Task.status != "Completed",
            (Task.earlieststarttime.is_(None) | (Task.earlieststarttime <= datetime.now())),
            (Task.repeatinterval.is_(None) | (Task.repeatinterval == min_sequence_subquery))
        )
        .order_by(Task.createdat.asc())
    )

    subtasks = session.execute(query).scalars().all()

    return subtasks


def get_subtasks_tree(session: Session, task_id: int):

    subtasks_tree = []

    if has_incomplete_subtask(session, task_id):
        subtasks = get_subtasks(session, task_id)  # Ensure `get_subtasks` exists

        for subtask_id in subtasks:
            subtasks_tree.extend(get_subtasks_tree(session, subtask_id))

    if not subtasks_tree:
        subtasks_tree.append(task_id)

    return subtasks_tree


def get_available_incomplete_tasks(session: Session):
    """Fetches tasks that are incomplete, available, and have no incomplete subtasks."""
    return session.query(Task.taskid, Task.taskname).filter(
        Task.status != 'Completed',
        Task.deleted == False,
        (Task.earlieststarttime == None) | (Task.earlieststarttime <= datetime.now()),
        ~session.query(Task.taskid).filter(
            Task.parenttaskid == Task.taskid,
            Task.status != 'Completed',
            Task.deleted == False
        ).exists()
    ).all()


def get_task_name(session: Session, task_id: int) -> Optional[str]:

    task = session.get(Task, task_id)
    return task.taskname if task else None


def get_task_by_id(session: Session, task_id: int) -> Optional[Dict[str, Any]]:
    return session.get(Task, task_id)


def get_tasks_by_ids(session: Session, task_id_list: List[int]) -> List[Dict[str, Any]]:
    from data.models.task_dependency_model import TaskDependencies

    if not task_id_list:
        return []

    # Query to fetch tasks that are not dependent tasks
    query = (
        select(Task)
        .where(
            Task.taskid.in_(task_id_list),
            ~Task.taskid.in_(  # Exclude tasks that exist in TaskDependencies as DependentTaskID
                select(TaskDependencies.dependenttaskid)
            )
        )
        .order_by(Task.taskname.asc())
    )

    tasks = session.execute(query).scalars().all()

    # Convert to list of dictionaries
    return [task.__dict__ for task in tasks]




def soft_delete_task(session: Session, task_id: int) -> bool:
    """
    Marks a task as deleted by setting 'deleted' to True and 'deleted_date' to the current timestamp.
    Returns True if the task was found and updated; otherwise, returns False.
    """
    task = session.get(Task, task_id)
    if not task or task.deleted:
        return False  # Task not found or already deleted

    task.deleted = True
    task.deleted_date = datetime.now()

    session.commit()
    return True


def update_earliest_start_time(session: Session, task_id: int, new_start_time: datetime) -> bool:
    task = session.get(Task, task_id)
    if task:
        task.earlieststarttime = new_start_time
        session.commit()
        return True
    return False


def mark_done(session: Session, task_id: int):
    session.execute(
        update(Task)
        .where(Task.taskid == task_id)
        .values(status="Completed", lastedittime=datetime.now())
    )
    session.commit()



def get_subtask_tree_ids(session: Session, task_id: int):
    # Recursively get all subtask ids
    subtasks = get_subtask_ids_all(session, task_id)
    all_subtasks = []
    for subtask in subtasks:
         all_subtasks.append(subtask)
         all_subtasks.extend(get_subtask_tree_ids(session, subtask))
    return all_subtasks



def add_workdays(start_date: datetime, days: int) -> datetime:
    current_date = start_date
    added = 0
    while added < days:
        current_date += timedelta(days=1)
        if current_date.weekday() < 5:  # Monday=0, Friday=4
            added += 1
    return current_date

def repeat_task(session: Session, task_id: int, yesterday=False):
    task = session.get(Task, task_id)
    if task and task.repeatinterval:
        base_time = datetime.now()
        if yesterday:
            base_time = base_time - timedelta(days=1)

        days = int(task.repeatinterval)
        # Add repeatinterval days, using workdays if repeatskipweekend is True.
        if task.repeatskipweekend:
            new_date = add_workdays(base_time, days)
        else:
            new_date = base_time + timedelta(days=days)

        # Parse repeattimeofday, which is stored as an integer (e.g., 900 for 09:00 or 1330 for 13:30)
        if task.repeattimeofday is not None:
            # Convert integer to a zero-padded 4-digit string (e.g., 900 becomes "0900")
            time_str = str(task.repeattimeofday).zfill(4)
            hour = int(time_str[:2])
            minute = int(time_str[2:])
            new_date = new_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        else:
            new_date = new_date.replace(hour=base_time.hour, minute=base_time.minute,
                                        second=base_time.second, microsecond=base_time.microsecond)

        new_task = Task(
            taskname=task.taskname,
            status="Pending",  # or your desired default status for a new task
            duedate=task.duedate,
            earlieststarttime=new_date,
            repeatinterval=task.repeatinterval,
            repeattimeofday=task.repeattimeofday,
            repeatskipweekend=task.repeatskipweekend,
            parenttaskid=task.parenttaskid,
            urgent=task.urgent,
            important=task.important,
            description=task.description,
            target=task.target,

        )
        session.add(new_task)

        # Copy tags
        new_task.tasktags = task.tasktags.copy()

        # Copy notes
        from data.models.task_note_model import TaskNote
        for note in task.tasknotes:
            new_note = TaskNote(taskid=new_task.taskid, note=note.note)
            session.add(new_note)


        session.commit()
        return new_task.taskid
    return None



def get_done_tasks(session: Session):
    return (
        session.query(Task)
        .filter(
            Task.status == "Completed",
            Task.deleted == False
        )
        .order_by(Task.lastedittime.desc())
        .limit(50)
        .all()
    )


def db_mark_task_done(session: Session, task_id: int, yesterday=False):
    # Retrieve the task
    task = session.get(Task, task_id)
    if not task:
        return None

    # If the task has a repeat interval, create a repeated task.
    new_task_id = None
    if task.repeatinterval:
        new_task_id = repeat_task(session, task_id, yesterday)

    # Mark the main task as done.
    mark_done(session, task_id)

    # Recursively mark all subtasks as done.
    subtask_ids = get_subtask_tree_ids(session, task_id)
    for stid in subtask_ids:
        mark_done(session, stid)

    return new_task_id





def get_next_task_to_work_on(session):
    from data.models.tag_model import TaskTag
    SubTask = aliased(Task)

    return (
        session.query(Task)
        .outerjoin(Task.tasktags)  # Ensure tasks without tags are included
        .filter(
            Task.status != "Completed",
            Task.deleted == False,
            or_(Task.earlieststarttime == None, Task.earlieststarttime < datetime.now()),
            ~exists().where(
                and_(
                    SubTask.parenttaskid == Task.taskid,
                    SubTask.status != "Completed",
                    SubTask.deleted == False
                )
            ),
            or_(
                TaskTag.name != "waiting",  # Exclude tasks tagged "waiting"
                TaskTag.name == None  # Include tasks with no tags
            )
        )
        .order_by(Task.urgent.desc(), Task.important.desc(), Task.taskid.asc())
        .first()
    )



def get_parent(session, task_id):
    task = session.get(Task, task_id)


    if task.parenttaskid:
        parent = session.get(Task, task.parenttaskid)
        if parent:
            return parent
        else:
            return None
    else:
        return None


def make_task_top_level(session: Session, task_id: int) -> bool:
    task = session.get(Task, task_id)
    if task:
        task.parenttaskid = None
        session.commit()
        return True
    return False


def get_available_incomplete_important_tasks(session: Session) -> list[Task]:
    """
    Returns a list of Task objects that are:
    - Not completed
    - Not deleted
    - Marked as important
    - Have no incomplete subtasks
    - Start time is either None or in the past
    """
    SubTask = aliased(Task)

    query = (
        session.query(Task)
        .filter(
            Task.status != "Completed",
            Task.deleted == False,
            Task.important == True,
            or_(Task.earlieststarttime == None, Task.earlieststarttime <= datetime.now()),
            ~exists().where(
                and_(
                    SubTask.parenttaskid == Task.taskid,
                    SubTask.status != "Completed",
                    SubTask.deleted == False
                )
            )
        )
        .order_by(Task.taskname.asc())
    )

    return query.all()


def get_available_incomplete_urgent_tasks(session: Session) -> list[Task]:
    """
    Returns a list of Task objects that are:
    - Not completed
    - Not deleted
    - Marked as important
    - Have no incomplete subtasks
    - Start time is either None or in the past
    """
    SubTask = aliased(Task)

    query = (
        session.query(Task)
        .filter(
            Task.status != "Completed",
            Task.deleted == False,
            Task.urgent == True,
            or_(Task.earlieststarttime == None, Task.earlieststarttime <= datetime.now()),
            ~exists().where(
                and_(
                    SubTask.parenttaskid == Task.taskid,
                    SubTask.status != "Completed",
                    SubTask.deleted == False
                )
            )
        )
        .order_by(Task.taskname.asc())
    )

    return query.all()


def set_task_important(session, task_id: int, is_important: bool) -> bool:
    task = session.get(Task, task_id)
    if task and not task.deleted:
        task.important = is_important
        session.commit()
        return True
    return False


def set_task_urgent(session, task_id: int, is_urgent: bool) -> bool:
    task = session.get(Task, task_id)
    if task and not task.deleted:
        task.urgent = is_urgent
        session.commit()
        return True
    return False

def is_task_important(session: Session, task_id: int) -> bool:
    task = session.get(Task, task_id)
    return bool(task and not task.deleted and task.important)


def is_task_urgent(session: Session, task_id: int) -> bool:
    task = session.get(Task, task_id)
    return bool(task and not task.deleted and task.urgent)


def crud_update_task_name(session: Session, task_id: int, new_name: str) -> bool:
    """
    Updates the name of the task with the given task_id.

    Args:
        session (Session): The SQLAlchemy session.
        task_id (int): The ID of the task to update.
        new_name (str): The new name for the task.

    Returns:
        bool: True if updated successfully, False otherwise.
    """
    task = session.get(Task, task_id)
    if task:
        task.taskname = new_name
        session.commit()
        return True
    return False


def update_task_sort_order(session: Session, task_id: int, new_sort_order: int) -> bool:
    """Updates the sort order of a given task."""
    task = session.get(Task, task_id)
    if task:
        task.sort_order = new_sort_order
        session.commit()
        return True
    return False

def crud_update_task_description(session: Session, task_id: int, new_description: str) -> bool:
    """
    Updates the description of the task with the given task_id.

    Args:
        session (Session): The SQLAlchemy session.
        task_id (int): The ID of the task to update.
        new_description (str): The new description for the task.

    Returns:
        bool: True if updated successfully, False otherwise.
    """
    task = session.get(Task, task_id)
    if task:
        task.description = new_description
        session.commit()
        return True
    return False


def crud_update_task_target(session: Session, task_id: int, new_target: str) -> bool:
    """
    Updates the description of the task with the given task_id.

    Args:
        session (Session): The SQLAlchemy session.
        task_id (int): The ID of the task to update.
        new_description (str): The new description for the task.

    Returns:
        bool: True if updated successfully, False otherwise.
    """
    task = session.get(Task, task_id)
    if task:
        task.target = new_target
        session.commit()
        return True
    return False


def crud_update_task_milestone(session: Session, task_id: int, new_milestone: str) -> bool:
    """
    Updates the milestone of the task with the given task_id.

    Args:
        session (Session): The SQLAlchemy session.
        task_id (int): The ID of the task to update.
        new_milestone (str): The new description for the task.

    Returns:
        bool: True if updated successfully, False otherwise.
    """
    task = session.get(Task, task_id)
    if task:
        task.milestone = new_milestone
        session.commit()
        return True
    return False



def update_task_parent(session: Session, task_id: int, new_parent_id: int) -> bool:
    """Updates the parent of a task to a new task ID."""
    task = session.get(Task, task_id)
    if task:
        task.parenttaskid = new_parent_id
        session.commit()
        return True
    return False




def get_recently_deleted_tasks(session: Session, days: int = 7) -> List[Task]:
    """
    Returns tasks that have been marked as deleted within the last `days` days.
    """
    cutoff = datetime.now() - timedelta(days=days)
    stmt = (
        select(Task)
        .where(
            Task.deleted == True,
            Task.deleted_date != None,
            Task.deleted_date >= cutoff
        )
        .order_by(Task.deleted_date.desc())
    )
    tasks = session.execute(stmt).scalars().all()
    return tasks

def undelete_task(session: Session, task_id: int) -> bool:
    """
    Undeletes a task by setting its deleted flag to False and clearing its deleted_date.
    Returns True if the task was successfully undeleted, otherwise False.
    """
    task = session.get(Task, task_id)
    if task and task.deleted:
        task.deleted = False
        task.deleted_date = None
        session.commit()
        return True
    return False


def update_task_repeat_interval(session, task_id: int, new_interval: int) -> bool:
    task = session.get(Task, task_id)
    if task:
        task.repeatinterval = new_interval
        session.commit()
        return True
    return False

def update_task_repeattimeofday(session, task_id: int, new_time: int) -> bool:
    task = session.get(Task, task_id)
    if task:
        task.repeattimeofday = new_time
        session.commit()
        return True
    return False

def update_task_repeatskipweekend(session, task_id: int, new_skip: bool) -> bool:
    task = session.get(Task, task_id)
    if task:
        task.repeatskipweekend = new_skip
        session.commit()
        return True
    return False



def get_task_target(session: Session, task_id: int):
    """
    Retrieves the target attribute from the Task model based on task_id.
    If any database error occurs or the task isn’t found, returns None.
    """
    try:
        task = session.get(Task, task_id)
        if task:
            return task.target  # Could be an empty string if not set
        return None
    except Exception as e:
        # Optionally, log the error here (e.g., logging.error(f"DB error in get_task_target: {e}"))
        return None


def get_task_milestone(session: Session, task_id: int):
    """
    Retrieves the target attribute from the Task model based on task_id.
    If any database error occurs or the task isn’t found, returns None.
    """
    try:
        task = session.get(Task, task_id)
        if task:
            return task.milestone  # Could be an empty string if not set
        return None
    except Exception as e:
        # Optionally, log the error here (e.g., logging.error(f"DB error in get_task_target: {e}"))
        return None

def mark_pending(session: Session, task_id: int):
    session.execute(
        update(Task)
        .where(Task.taskid == task_id)
        .values(status="Pending", lastedittime=datetime.now())
    )
    session.commit()
