<template>
  <div class="home-view">
    <el-container>
      <!-- 头部导航 -->
      <el-header class="header">
        <div class="header-content">
          <h1 class="title">
            <el-icon><Aim /></el-icon>
            提肛小助手
          </h1>
          <div class="nav-buttons">
            <el-button type="primary" @click="$router.push('/exercise')">
              <el-icon><VideoPlay /></el-icon>
              开始运动
            </el-button>
            <el-button @click="$router.push('/stats')">
              <el-icon><DataAnalysis /></el-icon>
              统计
            </el-button>
            <el-button @click="$router.push('/settings')">
              <el-icon><Setting /></el-icon>
              设置
            </el-button>
          </div>
        </div>
      </el-header>

      <!-- 主要内容 -->
      <el-main class="main-content">
        <!-- 快速状态卡片 -->
        <div class="status-cards">
          <el-card class="status-card">
            <div class="card-content">
              <el-icon class="card-icon today"><Calendar /></el-icon>
              <div class="card-info">
                <div class="card-value">{{ exerciseStore.stats.todayCount }}</div>
                <div class="card-label">今日次数</div>
              </div>
            </div>
          </el-card>

          <el-card class="status-card">
            <div class="card-content">
              <el-icon class="card-icon streak"><Trophy /></el-icon>
              <div class="card-info">
                <div class="card-value">{{ exerciseStore.stats.streakDays }}</div>
                <div class="card-label">连续天数</div>
              </div>
            </div>
          </el-card>

          <el-card class="status-card">
            <div class="card-content">
              <el-icon class="card-icon total"><DataBoard /></el-icon>
              <div class="card-info">
                <div class="card-value">{{ exerciseStore.stats.totalCount }}</div>
                <div class="card-label">总计次数</div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 提醒状态 -->
        <el-card class="reminder-card">
          <template #header>
            <div class="card-header">
              <span>提醒状态</span>
              <el-switch
                v-model="reminderEnabled"
                @change="handleReminderToggle"
                active-text="开启"
                inactive-text="关闭"
              />
            </div>
          </template>
          
          <div class="reminder-content">
            <div v-if="reminderEnabled" class="reminder-info">
              <p>
                <el-icon><Clock /></el-icon>
                下次提醒: {{ nextReminderText }}
              </p>
              <p>
                <el-icon><Timer /></el-icon>
                提醒间隔: {{ settingsStore.settings.reminderInterval }} 分钟
              </p>
            </div>
            <div v-else class="reminder-disabled">
              <el-icon><Bell /></el-icon>
              提醒已关闭
            </div>
          </div>
        </el-card>

        <!-- 快速开始 -->
        <div class="quick-start">
          <el-button
            type="primary"
            size="large"
            class="start-button"
            @click="quickStart"
            :loading="exerciseStore.loading"
            :disabled="!exerciseStore.canStartExercise"
          >
            <el-icon><VideoPlay /></el-icon>
            快速开始运动
          </el-button>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSettingsStore } from '@/stores/settings'
import { useExerciseStore } from '@/stores/exercise'
// 移除了Tauri store依赖
import { ElMessage } from 'element-plus'

const router = useRouter()
const settingsStore = useSettingsStore()
const exerciseStore = useExerciseStore()
// 移除了Tauri store实例

const reminderEnabled = ref(false)

// 计算属性
const nextReminderText = computed(() => {
  if (!exerciseStore.reminderStatus.nextReminder) return '未设置'
  
  const nextTime = new Date(exerciseStore.reminderStatus.nextReminder)
  const now = new Date()
  const diff = nextTime.getTime() - now.getTime()
  
  if (diff <= 0) return '即将提醒'
  
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) {
    return `${hours}小时${minutes % 60}分钟后`
  } else {
    return `${minutes}分钟后`
  }
})

// 方法
const handleReminderToggle = async () => {
  try {
    // 使用新的API调用
    const response = await exerciseStore.toggleReminderStatus()
    if (response.success) {
      reminderEnabled.value = response.data || false
      ElMessage.success(response.message)
    } else {
      ElMessage.error(response.message)
    }
  } catch (error) {
    ElMessage.error('切换提醒状态失败')
    reminderEnabled.value = !reminderEnabled.value // 回滚状态
  }
}

const quickStart = () => {
  router.push('/exercise')
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    settingsStore.loadSettings(),
    exerciseStore.loadStats(),
    exerciseStore.loadReminderStatus()
  ])

  // 设置提醒状态
  reminderEnabled.value = exerciseStore.reminderStatus.enabled
})
</script>

<style scoped>
.home-view {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.title {
  color: white;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
}

.nav-buttons {
  display: flex;
  gap: 10px;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.status-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: none;
  border-radius: 12px;
}

.card-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.card-icon {
  font-size: 32px;
  padding: 10px;
  border-radius: 8px;
}

.card-icon.today {
  background: #e3f2fd;
  color: #1976d2;
}

.card-icon.streak {
  background: #fff3e0;
  color: #f57c00;
}

.card-icon.total {
  background: #e8f5e8;
  color: #388e3c;
}

.card-info {
  flex: 1;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.card-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.reminder-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: none;
  border-radius: 12px;
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reminder-content {
  padding: 10px 0;
}

.reminder-info p {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0;
  color: #666;
}

.reminder-disabled {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #999;
  font-style: italic;
}

.quick-start {
  text-align: center;
}

.start-button {
  font-size: 18px;
  padding: 15px 40px;
  border-radius: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}
</style>
