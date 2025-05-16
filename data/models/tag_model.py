from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from typing import List, TYPE_CHECKING
from data.models.alchemy_base import Base

if TYPE_CHECKING:
    from data.models.task_model import Task

class TaskTag(Base):
    __tablename__ = "tasktags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    tasks: Mapped[List["Task"]] = relationship("Task", secondary="tasktaglinks", back_populates="tasktags")
