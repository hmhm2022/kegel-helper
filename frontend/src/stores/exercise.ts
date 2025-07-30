import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ExerciseStats, ExerciseRecord, ReminderStatus } from '@/types'
import { getStats, startExercise, completeExercise, getReminderStatus, toggleReminder } from '@/utils/api'

export const useExerciseStore = defineStore('exercise', () => {
  // 状态
  const stats = ref<ExerciseStats>({
    todayCount: 0,
    weekCount: 0,
    monthCount: 0,
    totalCount: 0,
    streakDays: 0
  })

  const currentExercise = ref<ExerciseRecord | null>(null)
  const reminderStatus = ref<ReminderStatus>({
    enabled: false,
    nextReminder: '',
    interval: 30
  })

  const isExercising = ref(false)
  const exerciseTimer = ref<number | null>(null)
  const currentRepetition = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const canStartExercise = computed(() => {
    return !isExercising.value && !loading.value
  })

  const exerciseProgress = computed(() => {
    if (!currentExercise.value || !isExercising.value) return 0
    return (currentRepetition.value / currentExercise.value.repetitions) * 100
  })

  // 动作
  const loadStats = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await getStats()
      if (response.data) {
        stats.value = response.data
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载统计数据失败'
      console.error('加载统计数据失败:', err)
    } finally {
      loading.value = false
    }
  }

  const loadReminderStatus = async () => {
    try {
      const response = await getReminderStatus()
      if (response.data) {
        reminderStatus.value = response.data
      }
    } catch (err) {
      console.error('加载提醒状态失败:', err)
    }
  }

  const beginExercise = async (duration: number, repetitions: number) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await startExercise()
      if (response.success) {
        currentExercise.value = {
          id: Date.now().toString(),
          startTime: new Date().toISOString(),
          endTime: '',
          duration,
          repetitions,
          completed: false
        }
        
        isExercising.value = true
        currentRepetition.value = 0
        
        return true
      } else {
        throw new Error(response.message || '开始运动失败')
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '开始运动失败'
      console.error('开始运动失败:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  const finishExercise = async (completed: boolean = true) => {
    try {
      if (!currentExercise.value) return false
      
      loading.value = true
      error.value = null
      
      const response = await completeExercise()
      if (response.success) {
        currentExercise.value.endTime = new Date().toISOString()
        currentExercise.value.completed = completed
        
        // 更新统计数据
        if (completed) {
          stats.value.todayCount++
          stats.value.totalCount++
        }
        
        // 重置状态
        isExercising.value = false
        currentExercise.value = null
        currentRepetition.value = 0
        
        if (exerciseTimer.value) {
          clearInterval(exerciseTimer.value)
          exerciseTimer.value = null
        }
        
        return true
      } else {
        throw new Error(response.message || '完成运动失败')
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '完成运动失败'
      console.error('完成运动失败:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  const incrementRepetition = () => {
    if (currentExercise.value && currentRepetition.value < currentExercise.value.repetitions) {
      currentRepetition.value++
    }
  }

  const resetExercise = () => {
    isExercising.value = false
    currentExercise.value = null
    currentRepetition.value = 0
    
    if (exerciseTimer.value) {
      clearInterval(exerciseTimer.value)
      exerciseTimer.value = null
    }
  }

  const toggleReminderStatus = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await toggleReminder()
      if (response.success && response.data !== undefined) {
        reminderStatus.value.enabled = response.data
      }
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : '切换提醒状态失败'
      console.error('切换提醒状态失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    stats,
    currentExercise,
    reminderStatus,
    isExercising,
    currentRepetition,
    loading,
    error,
    
    // 计算属性
    canStartExercise,
    exerciseProgress,
    
    // 动作
    loadStats,
    loadReminderStatus,
    toggleReminderStatus,
    beginExercise,
    finishExercise,
    incrementRepetition,
    resetExercise
  }
})
