from sqlalchemy import Column, Integer, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from app.database import Base

class Evaluation(Base):
    __tablename__ = "evaluation"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    eval_date = Column(Date, nullable=False)
    training_status = Column(Integer)  # 1~5
    fitness = Column(Integer)
    sleep = Column(Integer)
    appetite = Column(Integer)
    note = Column(Text)

    user = relationship("User", back_populates="evaluations")
