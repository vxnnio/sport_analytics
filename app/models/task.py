# app/models/task.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey,DateTime
from app.database import Base
from sqlalchemy.orm import relationship
from app.models.user import User
from datetime import datetime
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50))
    item = Column(String(100))
    description = Column(String(255))

    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    athlete_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    athlete = relationship("User", back_populates="tasks")
    
