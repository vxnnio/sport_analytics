from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from app.database import Base


class Evaluation(Base):
    __tablename__ = "evaluation"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    eval_date = Column(Date, default=date.today, nullable=False)
    training_status = Column(String(10))
    fitness = Column(String(10))
    sleep = Column(String(10))
    appetite = Column(String(10))
    note = Column(Text)

    user = relationship("User", back_populates="evaluations")
