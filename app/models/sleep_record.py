from sqlalchemy import Column, Integer, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class SleepRecord(Base):
    __tablename__ = 'sleep_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    athlete_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    record_date = Column(Date, nullable=False)
    sleep_start = Column(Time, nullable=False)
    sleep_end = Column(Time, nullable=False)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)




