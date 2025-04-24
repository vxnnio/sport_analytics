from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base


class Training(Base):
    __tablename__ = "training"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    date = Column(Date, nullable=False)
    jump_type = Column(String(50))
    jump_count = Column(Integer)
    run_distance = Column(Float)
    run_time = Column(String(20))
    weight_part = Column(String(50))
    weight_sets = Column(Integer)
    agility_type = Column(String(50))
    agility_note = Column(Text)
    special_focus = Column(Text)

    user = relationship("User", back_populates="trainings")
