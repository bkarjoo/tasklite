from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey
from data.models.alchemy_base import Base

class TaskTagLink(Base):
    __tablename__ = "tasktaglinks"

    tasktagid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    taskid: Mapped[int] = mapped_column(ForeignKey("tasks.taskid"), nullable=False)
    tagid: Mapped[int] = mapped_column(ForeignKey("tasktags.id"), nullable=False)
