from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.database import Base  # 你專案的 Base

class FoodPhoto(Base):
    __tablename__ = 'food_photos'
    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    athlete_username = Column(String(80), nullable=False) 
    filename = Column(String(255), nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    comment = Column(Text, nullable=True)
    comment_time = Column(DateTime, nullable=True)
