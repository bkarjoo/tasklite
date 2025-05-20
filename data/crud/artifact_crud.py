from sqlalchemy import or_

from data.models.artifact_model import Artifact
from data.models.task_artifact_model import TaskArtifact

def create_artifact(session, url: str):
    artifact_data = {"url": url}
    artifact = Artifact(**artifact_data)
    session.add(artifact)
    session.flush()
    return artifact


def get_artifact_by_id(session, artifact_id):
    """
    Retrieve an Artifact by its ID.
    """
    return session.query(Artifact).filter(Artifact.id == artifact_id).first()

def get_artifacts(session, skip=0, limit=100):
    """
    Retrieve a list of Artifacts with optional pagination.
    """
    return session.query(Artifact).offset(skip).limit(limit).all()

def update_artifact(session, artifact_id, update_data):
    """
    Update an existing Artifact with new data.
    Does not commit the change; commit should be handled by the caller.
    """
    artifact = get_artifact_by_id(session, artifact_id)
    if artifact is None:
        return None

    for key, value in update_data.items():
        if hasattr(artifact, key):
            setattr(artifact, key, value)

    session.flush()  # Flush changes to the session
    return artifact

def delete_artifact(session, artifact_id):
    """
    Delete an Artifact by its ID.
    Does not commit the change; commit should be handled by the caller.
    Returns True if the artifact was found and deleted, False otherwise.
    """
    artifact = get_artifact_by_id(session, artifact_id)
    if artifact is None:
        return False

    session.delete(artifact)
    session.flush()
    return True


# /Users/behroozkarjoo/dev/ai/db_layer/crud/artifacts.py
def get_artifact_types(session):
    """
    Retrieve distinct artifact types.
    """
    return session.query(Artifact.artifact_type).distinct().all()


def get_artifacts_by_wildcard(session, wildcard=None):
    query = session.query(Artifact)
    if wildcard:
        pattern = wildcard.replace('*', '%')
        print(f"pattern={pattern}")
        query = query.filter(Artifact.url.like(pattern))
    print(wildcard)
    print(query)
    res = query.all()
    print (res)
    return res


def create_task_artifact(session, taskid, artifact_id):
    link = TaskArtifact(taskid=taskid, artifact_id=artifact_id)
    session.add(link)
    session.flush()
    return link

def get_task_artifacts_by_task(session, taskid):
    return session.query(TaskArtifact).filter(TaskArtifact.taskid == taskid).all()

def get_tasks_by_artifact(session, artifact_id):
    return session.query(TaskArtifact).filter(TaskArtifact.artifact_id == artifact_id).all()

def delete_task_artifact(session, taskid, artifact_id):
    link = session.query(TaskArtifact).filter(
        TaskArtifact.taskid == taskid,
        TaskArtifact.artifact_id == artifact_id
    ).first()
    if not link:
        return False
    session.delete(link)
    session.flush()
    return True
