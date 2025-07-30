#!/usr/bin/env python3
"""
提肛小助手后端启动脚本
用于开发和测试
"""

import sys
import os
import subprocess
import logging

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'apscheduler'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")
    
    if missing_packages:
        print(f"\n缺少以下依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def start_server():
    """启动服务器"""
    try:
        print("🚀 正在启动提肛小助手后端服务...")
        
        # 检查依赖
        if not check_dependencies():
            return
        
        # 导入并启动应用
        import uvicorn

        # 启动服务器
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖都已正确安装")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 50)
    print("🎯 提肛小助手后端服务")
    print("=" * 50)
    
    start_server()
