from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from datetime import datetime

from data.models.task_model import Task
from data.models.alchemy_base import Base

class TaskNote(Base):
    __tablename__ = "tasknotes"

    noteid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    taskid: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.taskid"), nullable=False)
    note: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    task: Mapped["Task"] = relationship("Task", back_populates="tasknotes")
