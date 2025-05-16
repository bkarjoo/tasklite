from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey
from data.models.base import Base

class TaskDependencies(Base):
    __tablename__ = "taskdependencies"

    dependenttaskid: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.taskid", ondelete="CASCADE"), primary_key=True)
    blockingtaskid: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.taskid", ondelete="CASCADE"), primary_key=True)
