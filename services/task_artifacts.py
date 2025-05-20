from os import path

from data.crud.artifact_crud import (create_task_artifact,
                                     delete_task_artifact,
                                     get_task_artifacts_by_task,
                                     get_tasks_by_artifact)
from data.db_session import SessionLocal
from state.artifact_state import (get_artifact_list, set_artifact_list,
                                  set_selected_artifact)
from state.task_state import get_selected_task_id

from services.artifacts import get_artifact_service



def get_task_artifacts_by_task_service(task_id):
    with SessionLocal() as db:
        return get_task_artifacts_by_task(db, task_id)

def get_tasks_by_artifact_service(artifact_index):
    artifact_list = get_artifact_list()
    if 0 <= artifact_index < len(artifact_list):
        artifact_id = artifact_list[artifact_index].id
        with SessionLocal() as db:
            return get_tasks_by_artifact(db, artifact_id)
    return None

def delete_task_artifact_service(task_id, artifact_index):
    artifact_list = get_artifact_list()
    if 0 <= artifact_index < len(artifact_list):
        artifact_id = artifact_list[artifact_index].id
        with SessionLocal() as db:
            result = delete_task_artifact(db, task_id, artifact_id)
            if result:
                db.commit()
            return result
    return None



def create_task_artifact_service(artifact_index):
    task_id = get_selected_task_id()
    artifact_list = get_artifact_list()
    if 0 <= artifact_index < len(artifact_list):
        artifact_id = artifact_list[artifact_index].id
        with SessionLocal() as db:
            link = create_task_artifact(db, task_id, artifact_id)
            db.commit()
        return link
    return None

def create_task_artifact_by_id_service(artifact_id):
    task_id = get_selected_task_id()

    with SessionLocal() as db:
        link = create_task_artifact(db, task_id, artifact_id)
        db.commit()
    return link




def get_and_select_first_artifact_of_selected_task():
    task_id = get_selected_task_id()
    with SessionLocal() as db:
        artifact_links = get_task_artifacts_by_task(db, task_id)
    artifact_ids = [link.artifact_id for link in artifact_links]
    if artifact_ids:
        artifact_list = [get_artifact_service(artifact_id) for artifact_id in artifact_ids]
        set_artifact_list(artifact_list)
        for artifact in artifact_list:
            if path.isdir(artifact.url):
                set_selected_artifact(artifact)
                break

