from sqlalchemy import Column, Integer, String, Text, DateTime, func
from data.models.alchemy_base import Base

class Artifact(Base):
    __tablename__ = 'artifact'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=True)
    description = Column(Text)
    artifact_type = Column(String(100), nullable=True)
    url = Column(Text)  # Can be a local file path or a web URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
