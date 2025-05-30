from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Date, Boolean
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from app.database import Base

class Training(Base):
    __tablename__ = "training"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    date = Column(Date, nullable=False)

    # 體能訓練欄位
    jump_type = Column(String(50))
    jump_count = Column(Integer)
    run_distance = Column(Float)
    run_time = Column(String(20))
    weight_part = Column(String(50))
    weight_sets = Column(Integer)
    agility_type = Column(String(50))
    agility_note = Column(Text)
    special_focus = Column(Text)

    # 技巧訓練欄位（學生主動填）
    technical_title = Column(String(100))
    technical_items = Column(LONGTEXT)  # JSON array 格式
    technical_feedback = Column(Text)
    technical_completed = Column(Boolean, default=False)

    # ✅ 新增：教練派發內容
    coach_assigned_physical = Column(Text)              # 純文字（多行也可）
    coach_assigned_technical = Column(LONGTEXT)         # JSON array 格式（如 list of 技巧項目）

    # ✅ 新增：學生勾選完成狀態
    coach_physical_done = Column(Boolean, default=False)
    coach_technical_done = Column(Boolean, default=False)

    user = relationship("User", back_populates="trainings")