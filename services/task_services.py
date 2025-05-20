from datetime import datetime, timedelta

from data.crud.task_crud import (create_new_subtask, create_task,
                                 crud_update_task_milestone, db_mark_task_done,
                                 find_root_task_id,
                                 get_all_available_incomplete_tasks,
                                 get_all_available_incomplete_tasks_by_tag,
                                 get_available_incomplete_tasks,
                                 get_incomplete_available_important_tasks_ids,
                                 get_incomplete_available_urgent_tasks_ids,
                                 get_next_task_to_work_on, get_parent,
                                 get_root_tasks, get_root_tasks_all,
                                 get_task_by_id, get_task_milestone,
                                 get_tasks_by_ids, id_exists,
                                 is_task_important, is_task_urgent,
                                 make_task_top_level, mark_pending,
                                 root_task_search, set_task_important,
                                 set_task_urgent, soft_delete_task,
                                 task_read_subtasks,
                                 update_earliest_start_time)
from data.crud.task_tags_crud import get_tasks_by_tag_name
from data.models.tag_model import TaskTag
from state.task_state import (get_new_task_id,  set_new_task_id,
                              set_selected_task_id)
from utils.formatting import (format_future_tasks_as_list,
                              format_tasks_as_list_with_id)

from services.task_artifacts import get_and_select_first_artifact_of_selected_task
from services.task_tags import count_tasks_by_tag_service


def svc_get_task_by_id(task_id: int):
    with SessionLocal() as db:
        return get_task_by_id(db, task_id)



def set_task_ids_from_tasks(tasks):
    task_ids = [task.taskid for task in tasks]
    set_task_ids(task_ids)


def select_newly_created_task():
    new_task_id = get_new_task_id()
    if new_task_id:
        set_selected_task_id(get_new_task_id())
        return "Selected new task."
    else:
        return "No new task found."


def set_selected_task_id_confirm(task_id):
    try:
        id = int(task_id)

        with SessionLocal() as session:
            exists = id_exists(session, id)
        if exists:
            set_selected_task_id(id)
            return "Task selected successfully."
        else:
            return "Task not found."
    except:
        return "Invalid task id."


def set_selected_task_by_index(task_index):
    task_ids = get_task_ids()
    if task_ids:
        try:
            id = int(task_index)
        except:
            return "Invalid task index."
        if 1 <= id <= len(task_ids):
            set_selected_task_id(task_ids[id - 1])
            return "Task selected successfully."
        else:
            return "Task index out of range."
    else:
        return "No task selected."


def create_new_task(task_name: str) -> str:
    if len(task_name) > 100:
        task_name = task_name[:100]
        message = 'The task name was too long and has been truncated to 100 characters.\n'
    else:
        message = ''

    with SessionLocal() as session:
        task_id = create_task(session, task_name)

    set_new_task_id(task_id)

    if task_id:
        message += f'New task "{task_name} (id: {task_id})" added.'
    else:
        message += f'Add task "{task_name} Failed.'
    return message


def create_subtask_for_selected_task(task_name: str) -> str:
    with SessionLocal() as session:
        selected_task_id = get_selected_task_id()
        if selected_task_id:
            task = get_task_by_id(session, selected_task_id)
            if task.status == 'Completed':
                parent = get_parent(session, selected_task_id)
                if parent:
                    selected_task_id = parent.taskid
                else:
                    return "Cannot create subtask for completed task."



            subtask_id = create_new_subtask(session, selected_task_id, task_name)

            if subtask_id:
                set_new_task_id(subtask_id) # remember task id if user wants to select it

                return f"Subtask created successfully with ID: {subtask_id}"
        return "Failed to create subtask"


def get_root_task(task_id: int):
    """
    Retrieves the root task object for the given task_id by opening a new session,
    finding the root task's ID, and then fetching the full Task object.
    """
    with SessionLocal() as session:
        root_task_id = find_root_task_id(session, task_id)

        return session.get(Task, root_task_id)


def get_selected_tasks_root():
    selected_task_id = get_selected_task_id()
    if selected_task_id is None:
        return "No task selected."

    root_task = get_root_task(selected_task_id)
    if root_task is None:
        return "Root task not found."

    return f"Root Task: {root_task.taskname} (ID: {root_task.taskid})"


def get_task_roots_list(message):
    tag = None
    search_parameter = None
    if message and len(message) > 0:
        if '*' in message:
            search_parameter = message
        else:
            tag = message

    with SessionLocal() as session:
        if tag:
            tasks = get_tasks_by_tag_name(session, tag)
        elif search_parameter:
            tasks = root_task_search(session, f"{search_parameter.replace('*', '%')}%")
        else:
            tasks = get_root_tasks(session)

        formatted_list = format_tasks_as_list_with_id(tasks)

        set_task_ids_from_tasks(tasks)

        return formatted_list


def svc_get_future_tasks():
    from data.crud.task_crud import get_future_tasks

    with SessionLocal() as session:
        tasks = get_future_tasks(session)
        formatted_list = format_future_tasks_as_list(tasks)

        set_task_ids_from_tasks(tasks)

        return formatted_list


def svc_get_done_tasks():
    from data.crud.task_crud import get_done_tasks

    with SessionLocal() as session:
        tasks = get_done_tasks(session)
        formatted_list = format_tasks_as_list(tasks)

        set_task_ids_from_tasks(tasks)

        return formatted_list



def get_task_roots_list_all(message):
    tag = message
    # TODO tag filtering not implemented
    with SessionLocal() as session:
        tasks = get_root_tasks_all(session)
        formatted_list = format_future_tasks_as_list(tasks)

        set_task_ids_from_tasks(tasks)

        return formatted_list


def fetch_available_tasks():
    """Fetches available incomplete tasks from the database."""
    with SessionLocal() as session:
        return get_available_incomplete_tasks(session)


def fetch_store_and_return_tasks():
    """Fetches available incomplete tasks, stores them, and returns the list."""
    tasks = fetch_available_tasks()  # Fetch tasks from the database
    set_task_ids_from_tasks(tasks)  # Store tasks in the global list

    msg = ''
    if not tasks:
        msg = "No available tasks found."
        return msg

    formatted_tasks = format_tasks_as_list(tasks)
    formatted_task_list = formatted_tasks

    return formatted_task_list  # Return the raw list


def get_tree_view() -> str:
    selected_task_id = get_selected_task_id()


    if selected_task_id is None:
        return "No selected task to display tree view for."

    with SessionLocal() as session:
        root_id = find_root_task_id(session, selected_task_id)
        tree_view, _ = task_read_subtasks(session, selected_task_id, root_id)
    return tree_view


def mark_task_done():
    msg = ''
    task_id = get_selected_task_id()
    if task_id:
        with SessionLocal() as session:
            task = get_task_by_id(session, task_id)
            if task.status == "Completed":
                return "Task already marked complete."
            rowcount = db_mark_task_done(session, task_id)
            if rowcount == 0:
                msg += "Task not found or already completed."
            else:
                msg += "Task marked complete."
    else:
        msg += "No task selected."
    return msg


def mark_task_done_yesterday():
    msg = ''
    task_id = get_selected_task_id()
    if task_id:
        with SessionLocal() as session:
            task = get_task_by_id(session, task_id)
            if task.status == "Completed":
                return "Task already marked complete."
            rowcount = db_mark_task_done(session, task_id, yesterday=True)
            if rowcount == 0:
                msg += "Task not found or already completed."
            else:
                msg += "Task marked complete."
    else:
        msg += "No task selected."
    return msg



def what_to_do(tag=None):
    if tag == "":
        tag = None

    with SessionLocal() as session:
        task = get_next_task_to_work_on(session)
        if task:
            task_id = task.taskid
            set_selected_task_id(task_id)
            msg = task.print_as_stub()
            # session_id = get_session_by_task(session, task.taskid)
        else:
            msg = "No task to work on."
            return msg

    # if session_id:
    #     set_selected_session_id(session_id)
    # else:
    #     if get_message_count() > 0:
    #         start_new_session()

    # Append waiting count if greater than zero
    waiting_count = count_tasks_by_tag_service("waiting")
    if waiting_count > 0:
        msg += f"\n\nwaiting: {waiting_count}"

    get_and_select_first_artifact_of_selected_task()

    return msg


def optimal_task(message):
    msg = ''
    tag_name = message

    with SessionLocal() as session:
        if tag_name:
            task_ids = get_all_available_incomplete_tasks_by_tag(session, tag_name)
        else:
            task_ids = get_all_available_incomplete_tasks(session)

        urgent_ids = get_incomplete_available_urgent_tasks_ids(session, task_ids)
        important_ids = get_incomplete_available_important_tasks_ids(session, task_ids)

        working_list = []
        if urgent_ids:
            working_list = urgent_ids
        elif important_ids:
            working_list = important_ids
        else:
            working_list = task_ids

        tasks = get_tasks_by_ids(session, working_list)
        if not tasks:
            msg += "No tasks available to select from."
            return msg

        selected_task_id = min(working_list)
        selected_task = next(task for task in tasks if task['taskid'] == selected_task_id)
        set_selected_task_id(selected_task['taskid'])
        task_id = selected_task['taskid']
        root_id = find_root_task_id(session, task_id)

        tree_view, subtasks = task_read_subtasks(session, selected_task_id, root_id)

        # TODO show artifacts (attached files and sessions)
        arts = None

        if arts:
            msg = tree_view + '\n' + arts
        else:
            msg = tree_view

    return msg


def print_task_details():
    with SessionLocal() as session:
        task_id = get_selected_task_id()
        task = get_task_by_id(session, task_id)

        if task:
            return task.print_as_stub()
        else:
            return "No task selected."



def set_earliest_start_time(time_input: str):
    task_id = get_selected_task_id()
    if task_id is None:
        return "No task selected."

    with SessionLocal() as session:
        tokens = time_input.split()
        date_offset = 0
        time_of_day = datetime.min.time()

        for token in tokens:
            value = int(token)
            if value < 100:
                date_offset = value
            else:
                hours = value // 100
                minutes = value % 100
                time_of_day = datetime.min.replace(hour=hours, minute=minutes).time()

        new_start_time = (datetime.now() + timedelta(days=date_offset)).replace(
            hour=time_of_day.hour, minute=time_of_day.minute, second=0, microsecond=0
        )

        success = update_earliest_start_time(session, task_id, new_start_time)
        if success:
            return f"Earliest start time updated to {new_start_time}"
        else:
            return "Failed to update earliest start time."


def soft_delete(task_id):
    try:
        id = int(task_id)
    except:
        return "Invalid task id."
    with SessionLocal() as session:
        results = soft_delete_task(session, id)
        if results:
            return "Task deleted succssfully."
        else:
            return "Task deletion failed."


def select_parent():
    task_id = get_selected_task_id()

    if task_id is None:
        return "No task selected."

    with SessionLocal() as session:
        parent = get_parent(session, task_id)

    if parent:
        set_selected_task_id(parent.taskid)
        return f"Parent task {parent.taskid} selected."
    else:
        return "No parent found for selected task."


def get_task_list_urgent():
    from data.crud.task_crud import get_available_incomplete_urgent_tasks

    with SessionLocal() as session:
        tasks = get_available_incomplete_urgent_tasks(session)
        if not tasks:
            return "No urgent tasks found."
        set_task_ids_from_tasks(tasks)
        return format_tasks_as_list(tasks)


def get_task_list_important():
    from data.crud.task_crud import get_available_incomplete_important_tasks

    with SessionLocal() as session:
        tasks = get_available_incomplete_important_tasks(session)
        if not tasks:
            return "No important tasks found."
        set_task_ids_from_tasks(tasks)
        return format_tasks_as_list(tasks)





def svc_set_task_important(value: bool) -> str:
    task_id = get_selected_task_id()
    if task_id is None:
        return "No task selected."
    with SessionLocal() as session:
        success = set_task_important(session, task_id, value)
        return "Important flag updated." if success else "Failed to update important flag."


def svc_set_task_urgent(value: bool) -> str:
    task_id = get_selected_task_id()
    if task_id is None:
        return "No task selected."
    with SessionLocal() as session:
        success = set_task_urgent(session, task_id, value)
        return "Urgent flag updated." if success else "Failed to update urgent flag."


def svc_is_task_important() -> bool:
    task_id = get_selected_task_id()
    if task_id is None:
        return False
    with SessionLocal() as session:
        return is_task_important(session, task_id)


def svc_is_task_urgent() -> bool:
    task_id = get_selected_task_id()
    if task_id is None:
        return False
    with SessionLocal() as session:
        return is_task_urgent(session, task_id)

def elevate_task_to_top_level(task_id: int) -> str:
    with SessionLocal() as session:
        success = make_task_top_level(session, task_id)
        if success:
            return f"Task {task_id} is now a top-level task."
        else:
            return f"Failed to elevate task {task_id}."


from data.crud.task_crud import crud_update_task_name
from data.db_session import SessionLocal


def update_task_name_service(task_id: int, new_name: str) -> str:
    """
    Service function to update a task's name.

    Args:
        task_id (int): The ID of the task to update.
        new_name (str): The new name for the task.

    Returns:
        str: A message indicating success or failure.
    """
    with SessionLocal() as session:
        success = crud_update_task_name(session, task_id, new_name)
        if success:
            return f"Task {task_id} name updated to '{new_name}'."
        else:
            return f"Failed to update task {task_id}."


from data.crud.task_crud import update_task_sort_order
from data.db_session import SessionLocal


def update_task_sort_order_service(task_id: int, new_sort_order: int) -> str:
    with SessionLocal() as session:
        if update_task_sort_order(session, task_id, new_sort_order):
            return f"Task {task_id} sort order updated to {new_sort_order}."
        else:
            return f"Failed to update task {task_id} sort order."


from data.db_session import SessionLocal
from data.models.task_model import Task
from state.task_state import get_task_ids, set_task_ids


def move_task_by_index(src_index: int, dest_index: int) -> str:
    """
    Moves a task in the saved task list from the source index to the destination index.
    Indices are 1-based.
    Updates each task's sort_order in the database based on the new order.
    """
    # Retrieve the current saved task list (assumed to be a list of task IDs)
    task_ids = get_task_ids()
    if not task_ids:
        return "No tasks available to reorder."

    # Convert to 0-based indices
    src = src_index - 1
    dest = dest_index - 1

    if src < 0 or src >= len(task_ids) or dest < 0 or dest >= len(task_ids):
        return "Invalid index values."

    # Remove the task from its original position and insert it at the destination
    task_id = task_ids.pop(src)
    task_ids.insert(dest, task_id)

    # Update the sort_order for each task in the new order in one session
    with SessionLocal() as session:
        for order, tid in enumerate(task_ids, start=1):
            task = session.get(Task, tid)
            if task:
                task.sort_order = order
        session.commit()

    # Save the new order to the global state
    set_task_ids(task_ids)
    return f"Task moved from index {src_index} to {dest_index}."


from data.crud.task_crud import (crud_update_task_description,
                                 crud_update_task_target)
from data.db_session import SessionLocal


def update_task_description_service(task_id: int, new_description: str) -> str:
    with SessionLocal() as session:
        success = crud_update_task_description(session, task_id, new_description)
        if success:
            return f"Task {task_id} description updated."
        else:
            return f"Failed to update task {task_id} description."

def update_task_target_service(task_id: int, new_target: str) -> str:
    with SessionLocal() as session:
        success = crud_update_task_target(session, task_id, new_target)
        if success:
            return f"Task {task_id} target updated."
        else:
            return f"Failed to update task {task_id} target."


def update_task_milestone_service(task_id: int, new_milestone: str) -> str:
    with SessionLocal() as session:
        success = crud_update_task_milestone(session, task_id, new_milestone)
        if success:
            return f"Task {task_id} milestone updated."
        else:
            return f"Failed to update task {task_id} milestone."

from data.crud.task_crud import update_task_parent
from data.db_session import SessionLocal


def update_task_parent_service(task_id: int, new_parent_id: int) -> str:
    """Service wrapper to update the parent of a task."""
    with SessionLocal() as session:
        success = update_task_parent(session, task_id, new_parent_id)
        if success:
            return f"Parent updated: task {task_id} now has parent {new_parent_id}."
        else:
            return f"Failed to update parent for task {task_id}."



from data.crud.task_crud import get_recently_deleted_tasks
from data.db_session import SessionLocal
from state.task_state import set_task_ids
from utils.formatting import format_tasks_as_list


def fetch_recently_deleted_tasks(days: int = 7) -> str:
    """
    Fetches tasks that have been deleted within the last `days` days,
    saves their IDs to the state, formats the list using format_tasks_as_list,
    and returns the formatted string.
    """
    with SessionLocal() as session:
        tasks = get_recently_deleted_tasks(session, days)
        if not tasks:
            return f"No tasks have been deleted in the last {days} days."
        # Save the task IDs to state for uniformity.
        set_task_ids([task.taskid for task in tasks])
        return format_tasks_as_list(tasks)

from data.crud.task_crud import undelete_task
from data.db_session import SessionLocal


def undelete_task_service(task_id: int) -> str:
    """
    Service function that attempts to undelete a task.
    Returns a status message.
    """
    with SessionLocal() as session:
        if undelete_task(session, task_id):
            return f"Task {task_id} has been undeleted."
        else:
            return f"Failed to undelete task {task_id}."


from data.crud.task_crud import (update_task_repeat_interval,
                                 update_task_repeatskipweekend,
                                 update_task_repeattimeofday)
from data.db_session import SessionLocal
from state.task_state import get_selected_task_id


def update_repeat_interval_service(new_interval: int) -> str:
    task_id = get_selected_task_id()
    if not task_id:
        return "No task selected."
    with SessionLocal() as session:
        if update_task_repeat_interval(session, task_id, new_interval):
            return f"Repeat interval updated to {new_interval} days."
        else:
            return "Failed to update repeat interval."

def update_repeattimeofday_service(new_time: int) -> str:
    task_id = get_selected_task_id()
    if not task_id:
        return "No task selected."
    with SessionLocal() as session:
        if update_task_repeattimeofday(session, task_id, new_time):
            return f"Repeat time of day updated to {str(new_time).zfill(4)}."
        else:
            return "Failed to update repeat time of day."

def update_repeatskipweekend_service(new_skip: bool) -> str:
    task_id = get_selected_task_id()
    if not task_id:
        return "No task selected."
    with SessionLocal() as session:
        if update_task_repeatskipweekend(session, task_id, new_skip):
            return f"Repeat skip weekend updated to {new_skip}."
        else:
            return "Failed to update repeat skip weekend."


from data.crud.task_crud import get_task_target
from data.db_session import SessionLocal
from state.task_state import get_selected_task_id


def get_task_target_service() -> str:
    """
    Retrieves the target for the currently selected task.
    Manages the session and catches any database errors.
    Returns a user-friendly, formatted message.
    """
    task_id = get_selected_task_id()
    if not task_id:
        return "No task selected."

    try:
        with SessionLocal() as session:
            target = get_task_target(session, task_id)
            if target is None:
                return "Task not found or an error occurred."
            if target.strip() == "":
                return f"Task {task_id} has no target set."
            return f"Task {task_id} target: {target}"
    except Exception as e:
        # Optionally, log the exception details here
        return f"An error occurred when retrieving the task target: {str(e)}"


def get_task_milestone_service() -> str:
    """
    Retrieves the target for the currently selected task.
    Manages the session and catches any database errors.
    Returns a user-friendly, formatted message.
    """
    task_id = get_selected_task_id()
    if not task_id:
        return "No task selected."

    try:
        with SessionLocal() as session:
            milestone = get_task_milestone(session, task_id)
            if milestone is None:
                return "Task not found or an error occurred."
            if milestone.strip() == "":
                return f"Task {task_id} has no milestone set."
            return f"Task {task_id} milestone: {milestone}"
    except Exception as e:
        # Optionally, log the exception details here
        return f"An error occurred when retrieving the task milestone: {str(e)}"






def svc_project_stubs() -> str:
    """
    Fetches tasks that are tagged with "projects" and returns a stub
    representation of each task without including its notes.
    """
    with SessionLocal() as session:
        # Join tasktags and filter tasks having a tag with name "projects"
        project_tasks = (
            session.query(Task)
            .join(Task.tasktags)
            .filter(TaskTag.name == "projects")
            .all()
        )
        from data.crud.task_tags_crud import get_tasks_by_tag_name
        project_tasks = get_tasks_by_tag_name(session, 'project')

        def stub_text(task: Task) -> str:
            lines = []
            if task.taskname:
                lines.append(task.taskname)
                lines.append("-" * 22)
            if task.description:
                lines.append(task.description)
                lines.append("")
            if task.target:
                lines.append(f"wddli: {task.target}")
                lines.append("")
            if task.createdat:
                lines.append(f"**Created:** {task.createdat.strftime('%Y-%m-%d %H:%M')}")
                lines.append("")
            # if task.status:
            #     lines.append(f"**Status:** {task.status}")
            #     lines.append("")
            if task.taskid:
                lines.append(f"**id:** {task.taskid}")
                lines.append("")
            # Note: We intentionally skip any rendering of task notes.
            return "\n".join(lines).strip()

        stubs = [stub_text(task) for task in project_tasks]
        return "\n\n".join(stubs)


def set_task_pending():
    task_id = get_selected_task_id()
    if task_id:
        with SessionLocal() as session:
            mark_pending(session, task_id)
            return "Task status set to Pending."
    return "No task selected."
