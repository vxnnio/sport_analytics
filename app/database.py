from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import Config
from contextlib import contextmanager

# 定義基本模型
Base = declarative_base()

# 設定資料庫連線URL
DATABASE_URL = f"mysql+pymysql://{Config.DB_USERNAME}:{Config.DB_PASSWORD}@{Config.DB_HOST}/{Config.DB_NAME}"

# 建立資料庫引擎
engine = create_engine(DATABASE_URL, echo=False)

# 創建 sessionmaker，用於建立 session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 會話管理器
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db  # 這裡會返回 db 會話給呼叫者
    finally:
        db.close()  # 使用後自動關閉會話
