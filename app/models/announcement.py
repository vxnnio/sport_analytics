from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base  # 确保 Base 来自正确的 SQLAlchemy 配置

class Announcement(Base):
    __tablename__ = "announcement"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(20), nullable=False)
    coach_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    coach = relationship("User", back_populates="announcements")  # 确保 User 模型正确配置
