"""
统计数据服务
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Dict, List, Any

from models.database import ExerciseRecord, DailyStats

class StatsService:
    """统计数据服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_today_count(self) -> int:
        """获取今日运动次数"""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_stats = self.db.query(DailyStats).filter(DailyStats.date == today).first()
        return daily_stats.exercise_count if daily_stats else 0
    
    def get_week_count(self) -> int:
        """获取本周运动次数"""
        # 获取本周开始日期（周一）
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start_str = week_start.strftime("%Y-%m-%d")
        
        result = self.db.query(func.sum(DailyStats.exercise_count)).filter(
            DailyStats.date >= week_start_str
        ).scalar()
        
        return result if result else 0
    
    def get_month_count(self) -> int:
        """获取本月运动次数"""
        # 获取本月开始日期
        today = datetime.now()
        month_start = today.replace(day=1).strftime("%Y-%m-%d")
        
        result = self.db.query(func.sum(DailyStats.exercise_count)).filter(
            DailyStats.date >= month_start
        ).scalar()
        
        return result if result else 0
    
    def get_total_count(self) -> int:
        """获取总运动次数"""
        result = self.db.query(func.sum(DailyStats.exercise_count)).scalar()
        return result if result else 0
    
    def get_streak_days(self) -> int:
        """获取连续运动天数"""
        # 获取最近的每日统计记录，按日期倒序
        recent_stats = self.db.query(DailyStats).filter(
            DailyStats.exercise_count > 0
        ).order_by(DailyStats.date.desc()).all()
        
        if not recent_stats:
            return 0
        
        # 检查连续天数
        streak = 0
        today = datetime.now().date()
        
        for i, stat in enumerate(recent_stats):
            stat_date = datetime.strptime(stat.date, "%Y-%m-%d").date()
            expected_date = today - timedelta(days=i)
            
            if stat_date == expected_date:
                streak += 1
            else:
                break
        
        return streak
    
    def get_last_exercise_time(self) -> str:
        """获取最后运动时间"""
        last_record = self.db.query(ExerciseRecord).filter(
            ExerciseRecord.completed == True
        ).order_by(ExerciseRecord.end_time.desc()).first()
        
        if last_record and last_record.end_time:
            return last_record.end_time.isoformat()
        return ""
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """获取综合统计数据"""
        return {
            "todayCount": self.get_today_count(),
            "weekCount": self.get_week_count(),
            "monthCount": self.get_month_count(),
            "totalCount": self.get_total_count(),
            "streakDays": self.get_streak_days(),
            "lastExerciseTime": self.get_last_exercise_time()
        }
    
    def get_weekly_chart_data(self) -> List[Dict[str, Any]]:
        """获取本周图表数据"""
        # 获取本周7天的数据
        today = datetime.now()
        week_data = []
        
        for i in range(7):
            date = today - timedelta(days=6-i)
            date_str = date.strftime("%Y-%m-%d")
            
            daily_stats = self.db.query(DailyStats).filter(
                DailyStats.date == date_str
            ).first()
            
            week_data.append({
                "date": date_str,
                "dayName": date.strftime("%a"),
                "count": daily_stats.exercise_count if daily_stats else 0,
                "duration": daily_stats.total_duration if daily_stats else 0.0
            })
        
        return week_data
    
    def get_monthly_chart_data(self) -> List[Dict[str, Any]]:
        """获取本月图表数据"""
        today = datetime.now()
        month_start = today.replace(day=1)
        
        # 获取本月所有天数的数据
        month_data = []
        current_date = month_start
        
        while current_date.month == today.month:
            date_str = current_date.strftime("%Y-%m-%d")
            
            daily_stats = self.db.query(DailyStats).filter(
                DailyStats.date == date_str
            ).first()
            
            month_data.append({
                "date": date_str,
                "day": current_date.day,
                "count": daily_stats.exercise_count if daily_stats else 0,
                "duration": daily_stats.total_duration if daily_stats else 0.0
            })
            
            current_date += timedelta(days=1)
            if current_date > today:
                break
        
        return month_data
    
    def get_exercise_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取运动历史记录"""
        records = self.db.query(ExerciseRecord).filter(
            ExerciseRecord.completed == True
        ).order_by(ExerciseRecord.start_time.desc()).limit(limit).all()
        
        history = []
        for record in records:
            history.append({
                "id": record.id,
                "startTime": record.start_time.isoformat(),
                "endTime": record.end_time.isoformat() if record.end_time else "",
                "duration": record.duration,
                "plannedDuration": record.planned_duration,
                "repetitions": record.repetitions,
                "completed": record.completed
            })
        
        return history
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        # 计算平均运动时长
        avg_duration = self.db.query(func.avg(ExerciseRecord.duration)).filter(
            ExerciseRecord.completed == True
        ).scalar()
        
        # 计算完成率
        total_exercises = self.db.query(ExerciseRecord).count()
        completed_exercises = self.db.query(ExerciseRecord).filter(
            ExerciseRecord.completed == True
        ).count()
        
        completion_rate = (completed_exercises / total_exercises * 100) if total_exercises > 0 else 0
        
        # 计算本周平均每日运动次数
        week_count = self.get_week_count()
        avg_daily_this_week = week_count / 7
        
        return {
            "averageDuration": round(avg_duration, 2) if avg_duration else 0,
            "completionRate": round(completion_rate, 2),
            "averageDailyThisWeek": round(avg_daily_this_week, 2),
            "totalExercises": total_exercises,
            "completedExercises": completed_exercises
        }
