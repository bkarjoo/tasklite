from datetime import datetime

from data.models.task_note_model import TaskNote
from sqlalchemy.orm import Session


def create_task_note(session: Session, task_id: int, note_text: str) -> int:
    """
    Creates a new note for the given task.
    Returns the new note's ID.
    """
    new_note = TaskNote(taskid=task_id, note=note_text)
    session.add(new_note)
    session.commit()
    session.refresh(new_note)
    return new_note.noteid

def get_notes_by_task(session: Session, task_id: int):
    """
    Retrieves all notes associated with a given task.
    """
    return session.query(TaskNote).filter(TaskNote.taskid == task_id).order_by(TaskNote.created_at.asc()).all()

def update_task_note(session: Session, note_id: int, new_text: str) -> bool:
    """
    Updates the note text for a given note.
    """
    note = session.get(TaskNote, note_id)
    if note:
        note.note = new_text
        note.updated_at = datetime.utcnow()
        session.commit()
        return True
    return False

def delete_task_note(session: Session, note_id: int) -> bool:
    """
    Deletes a note by its ID.
    """
    note = session.get(TaskNote, note_id)
    if note:
        session.delete(note)
        session.commit()
        return True
    return False


def get_notes_by_ids(session: Session, note_ids: list[int]):
    return session.query(TaskNote).filter(TaskNote.noteid.in_(note_ids)).all()
