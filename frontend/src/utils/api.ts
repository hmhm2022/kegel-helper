import { invoke } from '@tauri-apps/api/tauri'
import type { UserSettings, ExerciseStats, ReminderStatus, ApiResponse } from '@/types'

// 检测是否在Tauri环境中
const isTauri = () => {
  return window.__TAURI__ !== undefined
}

// 通用的API调用函数
async function callApi<T>(command: string, args?: any): Promise<ApiResponse<T>> {
  if (isTauri()) {
    // 在Tauri环境中，使用invoke调用Rust命令
    try {
      const result = await invoke<ApiResponse<T>>(command, args)
      return result
    } catch (error) {
      console.error(`Tauri command ${command} failed:`, error)
      throw new Error(error as string)
    }
  } else {
    // 在开发环境中，可以返回模拟数据或调用开发服务器
    console.warn(`Tauri command ${command} called in non-Tauri environment`)
    throw new Error('此功能仅在桌面应用中可用')
  }
}

// 设置相关API
export const getSettings = (): Promise<ApiResponse<UserSettings>> => {
  return callApi<UserSettings>('get_settings')
}

export const updateSettings = (settings: UserSettings): Promise<ApiResponse<void>> => {
  return callApi<void>('update_settings', { settings })
}

// 统计数据相关API
export const getStats = (): Promise<ApiResponse<ExerciseStats>> => {
  return callApi<ExerciseStats>('get_stats')
}

// 运动相关API
export const startExercise = (): Promise<ApiResponse<string>> => {
  return callApi<string>('start_exercise')
}

export const completeExercise = (): Promise<ApiResponse<void>> => {
  return callApi<void>('complete_exercise')
}

// 提醒相关API
export const getReminderStatus = (): Promise<ApiResponse<ReminderStatus>> => {
  return callApi<ReminderStatus>('get_reminder_status')
}

export const toggleReminder = (): Promise<ApiResponse<boolean>> => {
  return callApi<boolean>('toggle_reminder')
}

export const checkAndSendReminder = (): Promise<ApiResponse<boolean>> => {
  return callApi<boolean>('check_and_send_reminder')
}

// 健康检查（在Tauri环境中不需要）
export const healthCheck = (): Promise<ApiResponse<void>> => {
  if (isTauri()) {
    return Promise.resolve({
      success: true,
      message: 'Tauri应用运行正常',
      data: undefined
    })
  } else {
    return Promise.reject(new Error('健康检查仅在桌面应用中可用'))
  }
}
