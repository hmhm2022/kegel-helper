<template>
  <div class="settings-view">
    <el-container>
      <!-- 头部 -->
      <el-header class="header">
        <div class="header-content">
          <el-button @click="$router.back()" type="text" class="back-btn">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <h2>设置</h2>
          <el-button @click="saveSettings" type="primary" :loading="settingsStore.loading">
            保存
          </el-button>
        </div>
      </el-header>

      <!-- 主要内容 -->
      <el-main class="main-content">
        <el-form :model="localSettings" label-width="120px" class="settings-form">
          
          <!-- 提醒设置 -->
          <el-card class="setting-card">
            <template #header>
              <div class="card-header">
                <el-icon><Bell /></el-icon>
                <span>提醒设置</span>
              </div>
            </template>
            
            <el-form-item label="提醒间隔">
              <el-slider
                v-model="localSettings.reminderInterval"
                :min="5"
                :max="120"
                :step="5"
                show-input
                :format-tooltip="formatMinutes"
              />
              <div class="form-help">每隔多长时间提醒一次运动（5-120分钟）</div>
            </el-form-item>

            <el-form-item label="工作时间限制">
              <el-switch v-model="localSettings.workingHours.enabled" />
              <div class="form-help">只在工作时间内发送提醒</div>
            </el-form-item>

            <el-form-item 
              v-if="localSettings.workingHours.enabled" 
              label="工作时间"
            >
              <div class="time-range">
                <el-time-picker
                  v-model="workingStartTime"
                  format="HH:mm"
                  placeholder="开始时间"
                />
                <span class="time-separator">至</span>
                <el-time-picker
                  v-model="workingEndTime"
                  format="HH:mm"
                  placeholder="结束时间"
                />
              </div>
            </el-form-item>

            <el-form-item label="启用通知">
              <el-switch v-model="localSettings.enableNotifications" />
              <div class="form-help">显示系统通知</div>
            </el-form-item>

            <el-form-item label="启用音效">
              <el-switch v-model="localSettings.enableSound" />
              <div class="form-help">播放提醒音效</div>
            </el-form-item>
          </el-card>

          <!-- 运动设置 -->
          <el-card class="setting-card">
            <template #header>
              <div class="card-header">
                <el-icon><Trophy /></el-icon>
                <span>运动设置</span>
              </div>
            </template>

            <el-form-item label="运动时长">
              <el-slider
                v-model="localSettings.exerciseDuration"
                :min="3"
                :max="30"
                show-input
                :format-tooltip="formatSeconds"
              />
              <div class="form-help">每次收缩持续时间（3-30秒）</div>
            </el-form-item>

            <el-form-item label="重复次数">
              <el-slider
                v-model="localSettings.repetitions"
                :min="5"
                :max="50"
                :step="5"
                show-input
                :format-tooltip="formatTimes"
              />
              <div class="form-help">每次运动的重复次数（5-50次）</div>
            </el-form-item>
          </el-card>

          <!-- 界面设置 -->
          <el-card class="setting-card">
            <template #header>
              <div class="card-header">
                <el-icon><Brush /></el-icon>
                <span>界面设置</span>
              </div>
            </template>

            <el-form-item label="主题">
              <el-radio-group v-model="localSettings.theme">
                <el-radio label="light">浅色主题</el-radio>
                <el-radio label="dark">深色主题</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-card>

          <!-- 数据管理 -->
          <el-card class="setting-card">
            <template #header>
              <div class="card-header">
                <el-icon><DataBoard /></el-icon>
                <span>数据管理</span>
              </div>
            </template>

            <el-form-item label="数据导出">
              <el-button @click="exportData" type="primary" plain>
                <el-icon><Download /></el-icon>
                导出运动数据
              </el-button>
              <div class="form-help">导出所有运动记录和统计数据</div>
            </el-form-item>

            <el-form-item label="重置数据">
              <el-button @click="showResetDialog" type="danger" plain>
                <el-icon><Delete /></el-icon>
                重置所有数据
              </el-button>
              <div class="form-help">清除所有运动记录和设置（不可恢复）</div>
            </el-form-item>
          </el-card>

        </el-form>
      </el-main>
    </el-container>

    <!-- 重置确认对话框 -->
    <el-dialog
      v-model="resetDialogVisible"
      title="确认重置"
      width="400px"
      center
    >
      <div class="reset-warning">
        <el-icon class="warning-icon"><WarningFilled /></el-icon>
        <p>此操作将清除所有运动记录和设置，且不可恢复。</p>
        <p>确定要继续吗？</p>
      </div>
      <template #footer>
        <el-button @click="resetDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="resetAllData">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useSettingsStore } from '@/stores/settings'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UserSettings } from '@/types'

const router = useRouter()
const settingsStore = useSettingsStore()

// 响应式数据
const localSettings = ref<UserSettings>({ ...settingsStore.settings })
const resetDialogVisible = ref(false)

// 时间选择器的值
const workingStartTime = ref<Date>(new Date())
const workingEndTime = ref<Date>(new Date())

// 计算属性
const formatMinutes = computed(() => {
  return (value: number) => `${value}分钟`
})

const formatSeconds = computed(() => {
  return (value: number) => `${value}秒`
})

const formatTimes = computed(() => {
  return (value: number) => `${value}次`
})

// 监听工作时间变化
watch([workingStartTime, workingEndTime], ([start, end]) => {
  if (start && end) {
    localSettings.value.workingHours.start = formatTime(start)
    localSettings.value.workingHours.end = formatTime(end)
  }
})

// 方法
const formatTime = (date: Date): string => {
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

const parseTime = (timeStr: string): Date => {
  const [hours, minutes] = timeStr.split(':').map(Number)
  const date = new Date()
  date.setHours(hours, minutes, 0, 0)
  return date
}

const saveSettings = async () => {
  try {
    const success = await settingsStore.saveSettings(localSettings.value)
    if (success) {
      ElMessage.success('设置保存成功')
    } else {
      ElMessage.error('设置保存失败')
    }
  } catch (error) {
    ElMessage.error('保存设置时出错')
  }
}

const exportData = async () => {
  try {
    // TODO: 实现数据导出功能
    ElMessage.info('数据导出功能开发中...')
  } catch (error) {
    ElMessage.error('导出数据失败')
  }
}

const showResetDialog = () => {
  resetDialogVisible.value = true
}

const resetAllData = async () => {
  try {
    // TODO: 实现数据重置功能
    settingsStore.resetSettings()
    localSettings.value = { ...settingsStore.settings }
    resetDialogVisible.value = false
    ElMessage.success('数据重置成功')
  } catch (error) {
    ElMessage.error('重置数据失败')
  }
}

// 生命周期
onMounted(async () => {
  await settingsStore.loadSettings()
  localSettings.value = { ...settingsStore.settings }
  
  // 初始化时间选择器
  workingStartTime.value = parseTime(localSettings.value.workingHours.start)
  workingEndTime.value = parseTime(localSettings.value.workingHours.end)
})
</script>

<style scoped>
.settings-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.header-content h2 {
  color: white;
  margin: 0;
}

.back-btn {
  color: white !important;
  font-size: 16px;
}

.main-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.settings-form {
  background: none;
}

.setting-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: none;
  border-radius: 16px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: bold;
  color: #333;
}

.form-help {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.time-range {
  display: flex;
  align-items: center;
  gap: 10px;
}

.time-separator {
  color: #666;
}

.reset-warning {
  text-align: center;
  padding: 20px;
}

.warning-icon {
  font-size: 48px;
  color: #f56c6c;
  margin-bottom: 15px;
}

.reset-warning p {
  margin: 10px 0;
  color: #666;
}

:deep(.el-form-item__label) {
  color: #333 !important;
  font-weight: 500;
}

:deep(.el-slider__runway) {
  background-color: #e4e7ed;
}

:deep(.el-slider__bar) {
  background-color: #409eff;
}

:deep(.el-slider__button) {
  border-color: #409eff;
}
</style>
