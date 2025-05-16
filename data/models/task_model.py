from typing import List, TYPE_CHECKING
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from data.models.alchemy_base import Base

if TYPE_CHECKING:
    from data.models.tag_model import TaskTag
    from data.models.task_note_model import TaskNote
    from data.models.task_tag_link_model import TaskTagLink

class Task(Base):
    __tablename__ = "tasks"

    taskid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    taskname: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, default="", nullable=True)
    target: Mapped[str] = mapped_column(String, default="", nullable=True)
    milestone: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    duedate: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    earlieststarttime: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    repeatinterval: Mapped[int] = mapped_column(Integer, nullable=True)
    repeattimeofday: Mapped[int] = mapped_column(DateTime, nullable=True)
    repeatskipweekend: Mapped[bool] = mapped_column(Boolean, nullable=True)
    parenttaskid: Mapped[int] = mapped_column(ForeignKey("tasks.taskid"), nullable=True)
    createdat: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    lastedittime: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    urgent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    important: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    parent_task: Mapped["Task"] = relationship("Task", remote_side=[taskid], backref="subtasks")
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=True)

    tasktags: Mapped[List["TaskTag"]] = relationship("TaskTag", secondary="tasktaglinks", back_populates="tasks")
    # Define the one-to-many relationship to TaskNote
    tasknotes: Mapped[List["TaskNote"]] = relationship(
        "TaskNote",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"  taskid={self.taskid},\n"
            f"  taskname={self.taskname},\n"
            f"  description={self.description},\n"
            f"  status={self.status},\n"
            f"  duedate={self.duedate},\n"
            f"  earlieststarttime={self.earlieststarttime},\n"
            f"  repeatinterval={self.repeatinterval},\n"
            f"  repeattimeofday={self.repeattimeofday},\n"
            f"  repeatskipweekend={self.repeatskipweekend},\n"
            f"  parenttaskid={self.parenttaskid},\n"
            f"  createdat={self.createdat},\n"
            f"  lastedittime={self.lastedittime},\n"
            f"  urgent={self.urgent},\n"
            f"  important={self.important},\n"
            f"  deleted={self.deleted},\n"
            f"  deleted_date={self.deleted_date},\n"
            f"  sort_order={self.sort_order}\n"
        )

    def print_as_stub(self) -> str:
        lines = []

        if getattr(self, "taskname", None):
            lines.append(f"{self.taskname}")
            lines.append("----------------------")

        if getattr(self, "description", None):
            lines.append(self.description)
            lines.append('\n')

        if getattr(self, "target", None):
            lines.append(f"wddli: {self.target}")
            lines.append('\n')

        if getattr(self, "milestone", None):
            lines.append(f"milestone: {self.milestone}")
            lines.append('\n')

        if getattr(self, "createdat", None):
            lines.append(f"**Created:** {self.createdat.strftime('%Y-%m-%d %H:%M')}")
            lines.append('\n')

        if getattr(self, "status", None):
            lines.append(f"**Status:** {self.status}")
            lines.append('\n')

        if hasattr(self, "tasknotes") and self.tasknotes:
            lines.append(f"**Note count: {len(self.tasknotes)}**")
        #     for note in self.tasknotes:
        #         if getattr(note, "note", None):
        #             created = note.created_at.strftime('%Y-%m-%d %H:%M') if note.created_at else ""
        #             lines.append(f"- {note.note}")

        return "\n".join(lines)
