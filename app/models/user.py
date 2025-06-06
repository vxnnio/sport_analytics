from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    bio = Column(String(500), default="")
    profile_pic = Column(String(255), default="static/uploads/default.png")

    full_name = Column(String(100), default="")
    birth_date = Column(Date, nullable=True)
    gender = Column(String(10), default="")  # 建議用 '男', '女', '其他'
    height = Column(Integer, nullable=True)  # 單位：公分
    weight = Column(Integer, nullable=True)  # 單位：公斤
    region = Column(String(100), default="")
    
    bio = Column(String(500), default="")
    profile_pic = Column(String(255), default="static/uploads/default.png")

    announcements = relationship("Announcement", back_populates="coach")
    trainings = relationship("Training", back_populates="user")
    evaluations = relationship("Evaluation", back_populates="user")

    # Flask-Login 需要的使用者方法
    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
