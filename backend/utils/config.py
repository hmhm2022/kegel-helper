"""
配置管理模块
"""

import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

from pydantic import Field

class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    APP_NAME: str = "提肛小助手"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # 服务器配置
    HOST: str = Field(default="127.0.0.1", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # 数据库配置
    DATABASE_URL: str = Field(default="sqlite:///./kegel_helper.db", env="DATABASE_URL")
    
    # 安全配置
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # 提醒配置
    DEFAULT_REMINDER_INTERVAL: int = Field(default=30, env="DEFAULT_REMINDER_INTERVAL")  # 分钟
    DEFAULT_EXERCISE_DURATION: int = Field(default=5, env="DEFAULT_EXERCISE_DURATION")  # 秒
    DEFAULT_EXERCISE_REPETITIONS: int = Field(default=10, env="DEFAULT_EXERCISE_REPETITIONS")
    
    # 系统托盘配置
    ENABLE_SYSTEM_TRAY: bool = Field(default=True, env="ENABLE_SYSTEM_TRAY")
    ENABLE_NOTIFICATIONS: bool = Field(default=True, env="ENABLE_NOTIFICATIONS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 创建全局配置实例
settings = Settings()

# 确保数据目录存在
def ensure_data_directory():
    """确保数据目录存在"""
    data_dir = os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", ""))
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)

# 初始化时创建数据目录
ensure_data_directory()
