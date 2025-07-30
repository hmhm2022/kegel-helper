// 用户设置接口
export interface UserSettings {
  reminderInterval: number // 提醒间隔（分钟）
  exerciseDuration: number // 运动持续时间（秒）
  repetitions: number // 重复次数
  enableSound: boolean // 启用音效
  enableNotifications: boolean // 启用通知
  theme: 'light' | 'dark' // 主题
  workingHours: {
    start: string // 工作开始时间
    end: string // 工作结束时间
    enabled: boolean // 是否启用工作时间限制
  }
}

// 运动统计接口
export interface ExerciseStats {
  todayCount: number // 今日次数
  weekCount: number // 本周次数
  monthCount: number // 本月次数
  totalCount: number // 总次数
  streakDays: number // 连续天数
  lastExerciseTime?: string // 最后运动时间
}

// 运动记录接口
export interface ExerciseRecord {
  id: string
  startTime: string
  endTime: string
  duration: number // 实际持续时间（秒）
  repetitions: number // 实际重复次数
  completed: boolean // 是否完成
}

// 提醒状态接口
export interface ReminderStatus {
  enabled: boolean // 是否启用
  nextReminder: string // 下次提醒时间
  interval: number // 间隔（分钟）
}

// API响应接口
export interface ApiResponse<T = any> {
  message: string
  data?: T
  success: boolean
}

// 动画配置接口
export interface AnimationConfig {
  duration: number // 动画持续时间
  easing: string // 缓动函数
  loop: boolean // 是否循环
}

// 主题配置接口
export interface ThemeConfig {
  primaryColor: string
  backgroundColor: string
  textColor: string
  borderColor: string
}
