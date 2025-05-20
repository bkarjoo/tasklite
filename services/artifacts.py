from data.crud.artifact_crud import (create_artifact, delete_artifact,
                                     get_artifact_by_id, get_artifact_types,
                                     get_artifacts, get_artifacts_by_wildcard,
                                     update_artifact)
from data.db_session import SessionLocal
from state.artifact_state import get_artifact_list, set_artifact_list


def create_artifact_service(url: str):
    with SessionLocal() as db:
        artifact = create_artifact(db, url)
        db.commit()
        return {"id": artifact.id, "url": artifact.url}


def get_artifact_service(artifact_id):
    with SessionLocal() as db:
        artifact = get_artifact_by_id(db, artifact_id)
    return artifact

def list_artifacts_service(skip=0, limit=100):
    with SessionLocal() as db:
        artifacts = get_artifacts(db, skip, limit)
    set_artifact_list(artifacts)
    return artifacts


def update_artifact_service(artifact_id, update_data):
    with SessionLocal() as db:
        artifact = update_artifact(db, artifact_id, update_data)
        if artifact is not None:
            db.commit()
    return artifact

def delete_artifact_service(artifact_id):
    with SessionLocal() as db:
        result = delete_artifact(db, artifact_id)
        if result:
            db.commit()
    return result

def delete_artifact_by_index_service(index):
    artifact_list = get_artifact_list()
    if 0 <= index < len(artifact_list):
        artifact = artifact_list[index]
        result = delete_artifact_service(artifact.id)
        return result, artifact.id
    return False, None


# /Users/behroozkarjoo/dev/ai/services/artifacts.py
def get_artifact_types_service():
    with SessionLocal() as db:
        types = get_artifact_types(db)
    return [t[0] for t in types if t[0] is not None]


def list_artifacts_by_wildcard_service(wildcard=None):
    print(wildcard)
    with SessionLocal() as db:
        artifacts = get_artifacts_by_wildcard(db, wildcard)
    set_artifact_list(artifacts)
    return artifacts


