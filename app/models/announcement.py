from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base  # 假设你的 Base 是从 sqlalchemy.ext.declarative 中创建的

class Announcement(Base):
    __tablename__ = "announcement"
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(20), nullable=False)
    coach_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    coach = relationship("User", back_populates="announcements")  # 确保有正确的 User 模型配置
