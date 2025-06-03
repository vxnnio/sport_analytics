# app/models/attendance.py

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database import Base  # 若你使用 declarative_base()

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String(10), nullable=False)  # present / absent / late

