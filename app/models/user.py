from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    
    line_user_id = Column(String(128), unique=True, nullable=True)

    full_name = Column(String(100), default="")
    birth_date = Column(Date, nullable=True)
    gender = Column(String(10), default="")  # 建議用 '男', '女', '其他'
    height = Column(Integer, nullable=True)  # 單位：公分
    weight = Column(Integer, nullable=True)  # 單位：公斤
    region = Column(String(100), default="")
    
    bio = Column(String(500), default="")
    profile_pic = Column(String(255), default="uploads/default.png")

    # 資料關聯
    announcements = relationship("Announcement", back_populates="coach")
    evaluations = relationship("Evaluation", back_populates="user")
    stress_evaluate = relationship("StressEvaluate", back_populates="athlete")  # ✅ 新增：壓力評估資料
    tasks = relationship("Task", back_populates="athlete")  # ✅ 改用 Task

    # Flask-Login 所需方法
    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

