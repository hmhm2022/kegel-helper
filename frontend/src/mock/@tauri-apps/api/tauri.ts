// Mock Tauri API for development
export const invoke = async (command: string, args?: any) => {
  console.log(`Mock Tauri invoke: ${command}`, args)

  // Mock responses for different commands
  switch (command) {
    case 'start_exercise':
      return {
        success: true,
        message: "运动开始",
        data: new Date().toISOString()
      }
    case 'complete_exercise':
      return {
        success: true,
        message: "运动完成",
        data: null
      }
    case 'get_stats':
      return {
        success: true,
        message: "统计数据获取成功",
        data: {
          todayCount: 0,
          weekCount: 0,
          monthCount: 0,
          totalCount: 0,
          streakDays: 0
        }
      }
    case 'get_settings':
      return {
        success: true,
        message: "设置获取成功",
        data: {
          exerciseDuration: 5,
          repetitions: 10,
          reminderInterval: 30,
          soundEnabled: true,
          vibrationEnabled: true
        }
      }
    case 'update_settings':
      return {
        success: true,
        message: "设置更新成功",
        data: null
      }
    case 'get_reminder_status':
      return {
        success: true,
        message: "提醒状态获取成功",
        data: {
          enabled: false,
          nextReminder: '',
          interval: 30
        }
      }
    case 'toggle_reminder':
      return {
        success: true,
        message: "提醒状态切换成功",
        data: true
      }
    case 'show_notification':
      return {
        success: true,
        message: "通知显示成功",
        data: null
      }
    case 'minimize_to_tray':
      return {
        success: true,
        message: "最小化到托盘成功",
        data: null
      }
    case 'show_from_tray':
      return {
        success: true,
        message: "从托盘显示成功",
        data: null
      }
    case 'register_global_shortcut':
      return {
        success: true,
        message: "全局快捷键注册成功",
        data: null
      }
    default:
      return {
        success: true,
        message: "命令执行成功",
        data: null
      }
  }
}
