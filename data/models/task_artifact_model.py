from sqlalchemy import Column, Integer, ForeignKey
from data.models.alchemy_base import Base


class TaskArtifact(Base):
    __tablename__ = 'task_artifact'

    taskid = Column(Integer, ForeignKey('tasks.taskid', ondelete='CASCADE'), primary_key=True)
    artifact_id = Column(Integer, ForeignKey('artifact.id', ondelete='CASCADE'), primary_key=True)
