from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    role = Column(String(20), nullable=False)

    announcements = relationship("Announcement", back_populates="coach")
    trainings = relationship("Training", back_populates="user")
    evaluations = relationship("Evaluation", back_populates="user")
