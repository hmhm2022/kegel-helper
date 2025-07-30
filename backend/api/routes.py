"""
API路由定义
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime, timedelta
import json

from models.database import get_db, UserSettings, ExerciseRecord, DailyStats, ReminderLog
from services.scheduler import SchedulerService
from services.stats import StatsService
from utils.config import settings

# 创建路由器
router = APIRouter()

# 全局调度器实例
scheduler_service = SchedulerService()

@router.get("/")
async def api_root():
    """API根路径"""
    return {"message": "提肛小助手 API v1.0"}

@router.get("/settings")
async def get_settings(db: Session = Depends(get_db)):
    """获取用户设置"""
    try:
        user_settings = db.query(UserSettings).first()
        if not user_settings:
            # 创建默认设置
            user_settings = UserSettings()
            db.add(user_settings)
            db.commit()
            db.refresh(user_settings)

        return {
            "success": True,
            "data": {
                "reminderInterval": user_settings.reminder_interval,
                "exerciseDuration": user_settings.exercise_duration,
                "repetitions": user_settings.repetitions,
                "enableSound": user_settings.enable_sound,
                "enableNotifications": user_settings.enable_notifications,
                "theme": user_settings.theme,
                "workingHours": {
                    "start": user_settings.working_hours_start,
                    "end": user_settings.working_hours_end,
                    "enabled": user_settings.working_hours_enabled
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设置失败: {str(e)}")

@router.post("/settings")
async def update_settings(settings_data: Dict[str, Any], db: Session = Depends(get_db)):
    """更新用户设置"""
    try:
        user_settings = db.query(UserSettings).first()
        if not user_settings:
            user_settings = UserSettings()
            db.add(user_settings)

        # 更新设置
        if "reminderInterval" in settings_data:
            user_settings.reminder_interval = settings_data["reminderInterval"]
        if "exerciseDuration" in settings_data:
            user_settings.exercise_duration = settings_data["exerciseDuration"]
        if "repetitions" in settings_data:
            user_settings.repetitions = settings_data["repetitions"]
        if "enableSound" in settings_data:
            user_settings.enable_sound = settings_data["enableSound"]
        if "enableNotifications" in settings_data:
            user_settings.enable_notifications = settings_data["enableNotifications"]
        if "theme" in settings_data:
            user_settings.theme = settings_data["theme"]

        # 更新工作时间设置
        if "workingHours" in settings_data:
            working_hours = settings_data["workingHours"]
            if "start" in working_hours:
                user_settings.working_hours_start = working_hours["start"]
            if "end" in working_hours:
                user_settings.working_hours_end = working_hours["end"]
            if "enabled" in working_hours:
                user_settings.working_hours_enabled = working_hours["enabled"]

        user_settings.updated_at = datetime.utcnow()
        db.commit()

        # 更新提醒任务
        if "reminderInterval" in settings_data:
            scheduler_service.add_reminder_job(settings_data["reminderInterval"])

        return {"success": True, "message": "设置已更新"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新设置失败: {str(e)}")

@router.get("/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """获取运动统计数据"""
    try:
        stats_service = StatsService(db)
        stats = stats_service.get_comprehensive_stats()

        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

@router.post("/exercise/start")
async def start_exercise(db: Session = Depends(get_db)):
    """开始运动"""
    try:
        # 获取用户设置
        user_settings = db.query(UserSettings).first()
        if not user_settings:
            raise HTTPException(status_code=404, detail="用户设置不存在")

        # 创建运动记录
        exercise_record = ExerciseRecord(
            start_time=datetime.utcnow(),
            planned_duration=user_settings.exercise_duration,
            repetitions=user_settings.repetitions,
            completed=False
        )
        db.add(exercise_record)
        db.commit()
        db.refresh(exercise_record)

        return {
            "success": True,
            "message": "运动开始",
            "data": {
                "exerciseId": exercise_record.id,
                "startTime": exercise_record.start_time.isoformat(),
                "plannedDuration": exercise_record.planned_duration,
                "repetitions": exercise_record.repetitions
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"开始运动失败: {str(e)}")

@router.post("/exercise/complete")
async def complete_exercise(exercise_data: Dict[str, Any] = None, db: Session = Depends(get_db)):
    """完成运动"""
    try:
        # 获取最近的未完成运动记录
        exercise_record = db.query(ExerciseRecord).filter(
            ExerciseRecord.completed == False
        ).order_by(ExerciseRecord.start_time.desc()).first()

        if not exercise_record:
            raise HTTPException(status_code=404, detail="没有找到进行中的运动记录")

        # 更新运动记录
        end_time = datetime.utcnow()
        exercise_record.end_time = end_time
        exercise_record.duration = (end_time - exercise_record.start_time).total_seconds()
        exercise_record.completed = True

        # 更新每日统计
        today = datetime.now().strftime("%Y-%m-%d")
        daily_stats = db.query(DailyStats).filter(DailyStats.date == today).first()

        if not daily_stats:
            daily_stats = DailyStats(date=today, exercise_count=1, total_duration=exercise_record.duration)
            db.add(daily_stats)
        else:
            daily_stats.exercise_count += 1
            daily_stats.total_duration += exercise_record.duration
            daily_stats.updated_at = datetime.utcnow()

        db.commit()

        return {
            "success": True,
            "message": "运动完成",
            "data": {
                "exerciseId": exercise_record.id,
                "duration": exercise_record.duration,
                "todayCount": daily_stats.exercise_count
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"完成运动失败: {str(e)}")

@router.get("/reminder/status")
async def get_reminder_status():
    """获取提醒状态"""
    try:
        return {
            "success": True,
            "data": {
                "enabled": scheduler_service.is_reminder_enabled(),
                "nextReminder": scheduler_service.get_next_reminder_time(),
                "interval": 30  # TODO: 从设置中获取
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取提醒状态失败: {str(e)}")

@router.post("/reminder/toggle")
async def toggle_reminder(db: Session = Depends(get_db)):
    """切换提醒开关"""
    try:
        user_settings = db.query(UserSettings).first()
        if not user_settings:
            raise HTTPException(status_code=404, detail="用户设置不存在")

        if scheduler_service.is_reminder_enabled():
            scheduler_service.remove_reminder_job()
            enabled = False
        else:
            scheduler_service.add_reminder_job(user_settings.reminder_interval)
            enabled = True

        return {
            "success": True,
            "message": f"提醒已{'开启' if enabled else '关闭'}",
            "data": {"enabled": enabled}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切换提醒状态失败: {str(e)}")
