"""
数据库模型定义
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

from utils.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

class UserSettings(Base):
    """用户设置表"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    reminder_interval = Column(Integer, default=30)  # 提醒间隔（分钟）
    exercise_duration = Column(Integer, default=5)   # 运动持续时间（秒）
    repetitions = Column(Integer, default=10)        # 重复次数
    enable_sound = Column(Boolean, default=True)     # 启用音效
    enable_notifications = Column(Boolean, default=True)  # 启用通知
    theme = Column(String(20), default="light")      # 主题
    working_hours_start = Column(String(10), default="09:00")  # 工作开始时间
    working_hours_end = Column(String(10), default="18:00")    # 工作结束时间
    working_hours_enabled = Column(Boolean, default=True)      # 启用工作时间限制
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExerciseRecord(Base):
    """运动记录表"""
    __tablename__ = "exercise_records"
    
    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)  # 实际持续时间（秒）
    planned_duration = Column(Integer, default=5)  # 计划持续时间（秒）
    repetitions = Column(Integer, default=10)  # 重复次数
    completed = Column(Boolean, default=False)  # 是否完成
    created_at = Column(DateTime, default=datetime.utcnow)

class DailyStats(Base):
    """每日统计表"""
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), unique=True, index=True)  # YYYY-MM-DD格式
    exercise_count = Column(Integer, default=0)  # 当日运动次数
    total_duration = Column(Float, default=0.0)  # 当日总运动时间（秒）
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReminderLog(Base):
    """提醒日志表"""
    __tablename__ = "reminder_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    reminder_time = Column(DateTime, default=datetime.utcnow)
    responded = Column(Boolean, default=False)  # 是否响应了提醒
    response_time = Column(DateTime, nullable=True)  # 响应时间
    created_at = Column(DateTime, default=datetime.utcnow)

# 创建所有表
def create_tables():
    """创建数据库表"""
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库
def init_database():
    """初始化数据库"""
    create_tables()
    
    # 创建默认设置
    db = SessionLocal()
    try:
        # 检查是否已有设置
        existing_settings = db.query(UserSettings).first()
        if not existing_settings:
            default_settings = UserSettings()
            db.add(default_settings)
            db.commit()
            print("✅ 已创建默认用户设置")
    except Exception as e:
        print(f"❌ 初始化数据库失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
