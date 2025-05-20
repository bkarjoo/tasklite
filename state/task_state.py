_task_ids = None

def set_task_ids(task_ids):
    global _task_ids
    _task_ids = task_ids

def get_task_ids():
    return _task_ids

_new_task_id = None

def set_new_task_id(task_id: int):
    global _new_task_id
    _new_task_id = task_id

def get_new_task_id() -> int | None:
    return _new_task_id

_selected_task_id = None

def get_selected_task_id() -> int | None:
    return _selected_task_id

def set_selected_task_id(task_id: int):
    global _selected_task_id
    _selected_task_id = task_id

_multi_select = None

def set_multi_select(task_ids):
    global _multi_select
    _multi_select = task_ids

def get_multi_select():
    return _multi_select
