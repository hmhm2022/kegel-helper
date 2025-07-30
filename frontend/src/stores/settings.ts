import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserSettings } from '@/types'
import { getSettings, updateSettings } from '@/utils/api'

export const useSettingsStore = defineStore('settings', () => {
  // 状态
  const settings = ref<UserSettings>({
    reminderInterval: 30,
    exerciseDuration: 5,
    repetitions: 10,
    enableSound: true,
    enableNotifications: true,
    theme: 'light',
    workingHours: {
      start: '09:00',
      end: '18:00',
      enabled: true
    }
  })

  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const isWorkingTime = computed(() => {
    if (!settings.value.workingHours.enabled) return true
    
    const now = new Date()
    const currentTime = now.getHours() * 60 + now.getMinutes()
    
    const [startHour, startMin] = settings.value.workingHours.start.split(':').map(Number)
    const [endHour, endMin] = settings.value.workingHours.end.split(':').map(Number)
    
    const startTime = startHour * 60 + startMin
    const endTime = endHour * 60 + endMin
    
    return currentTime >= startTime && currentTime <= endTime
  })

  // 动作
  const loadSettings = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await getSettings()
      if (response.data) {
        settings.value = { ...settings.value, ...response.data }
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载设置失败'
      console.error('加载设置失败:', err)
    } finally {
      loading.value = false
    }
  }

  const saveSettings = async (newSettings: Partial<UserSettings>) => {
    try {
      loading.value = true
      error.value = null
      
      const updatedSettings = { ...settings.value, ...newSettings }
      const response = await updateSettings(updatedSettings)
      
      if (response.success) {
        settings.value = updatedSettings
        return true
      } else {
        throw new Error(response.message || '保存设置失败')
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '保存设置失败'
      console.error('保存设置失败:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  const resetSettings = () => {
    settings.value = {
      reminderInterval: 30,
      exerciseDuration: 5,
      repetitions: 10,
      enableSound: true,
      enableNotifications: true,
      theme: 'light',
      workingHours: {
        start: '09:00',
        end: '18:00',
        enabled: true
      }
    }
  }

  return {
    // 状态
    settings,
    loading,
    error,
    
    // 计算属性
    isWorkingTime,
    
    // 动作
    loadSettings,
    saveSettings,
    resetSettings
  }
})
