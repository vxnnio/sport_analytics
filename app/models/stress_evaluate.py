# app/models/stress_record.py

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class StressEvaluate(Base):
    __tablename__ = "stress_evaluate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    athlete_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # 17 題題目
    q1 = Column(Integer)
    q2 = Column(Integer)
    q3 = Column(Integer)
    q4 = Column(Integer)
    q5 = Column(Integer)
    q6 = Column(Integer)
    q7 = Column(Integer)
    q8 = Column(Integer)
    q9 = Column(Integer)
    q10 = Column(Integer)
    q11 = Column(Integer)
    q12 = Column(Integer)
    q13 = Column(Integer)
    q14 = Column(Integer)
    q15 = Column(Integer)
    q16 = Column(Integer)
    q17 = Column(Integer)

    athlete = relationship("User", back_populates="stress_evaluate")
