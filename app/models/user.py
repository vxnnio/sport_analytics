from sqlalchemy import Column, Integer, String
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

    announcements = relationship("Announcement", back_populates="coach")
    trainings = relationship("Training", back_populates="user")
    evaluations = relationship("Evaluation", back_populates="user")
    # Flask-Login 需要的使用者方法
    def is_active(self):
        return True  # 默認所有使用者都是活躍的

    def is_authenticated(self):
        return True  # 可以根據需要調整

    def is_anonymous(self):
        return False  # 可以根據需要調整

    def get_id(self):
        return str(self.id)  # Flask-Login 用於識別使用者的 ID
