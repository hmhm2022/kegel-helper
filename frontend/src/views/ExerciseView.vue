<template>
  <div class="exercise-view">
    <el-container>
      <!-- 头部 -->
      <el-header class="header">
        <div class="header-content">
          <el-button @click="$router.back()" type="text" class="back-btn">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <h2>运动指导</h2>
          <div></div>
        </div>
      </el-header>

      <!-- 主要内容 -->
      <el-main class="main-content">
        <!-- 运动状态卡片 -->
        <el-card class="exercise-card">
          <div v-if="!exerciseStore.isExercising" class="exercise-ready">
            <div class="exercise-info">
              <h3>准备开始提肛运动</h3>
              <div class="exercise-params">
                <div class="param-item">
                  <el-icon><Timer /></el-icon>
                  <span>持续时间: {{ settingsStore.settings.exerciseDuration }}秒</span>
                </div>
                <div class="param-item">
                  <el-icon><Refresh /></el-icon>
                  <span>重复次数: {{ settingsStore.settings.repetitions }}次</span>
                </div>
              </div>
            </div>
            
            <!-- 动作指导 -->
            <div class="exercise-guide">
              <h4>动作要领</h4>
              <ol class="guide-steps">
                <li>坐直或站立，保持背部挺直</li>
                <li>收紧腹部，想象夹断"粑粑"的感觉</li>
                <li>吸气时收缩肛门肌肉，坚持3-5秒</li>
                <li>呼气时放松肌肉，休息3-5秒</li>
                <li>重复以上动作</li>
              </ol>
            </div>

            <el-button 
              type="primary" 
              size="large" 
              class="start-btn"
              @click="startExercise"
              :loading="exerciseStore.loading"
            >
              <el-icon><VideoPlay /></el-icon>
              开始运动
            </el-button>
          </div>

          <!-- 运动进行中 -->
          <div v-else class="exercise-active">
            <!-- 呼吸指导动画组件 -->
            <BreathingAnimation
              :is-active="exerciseStore.isExercising"
              :cycle-duration="8"
              :show-progress="true"
              :total-cycles="settingsStore.settings.repetitions"
              :current-cycle="exerciseStore.currentRepetition"
              @cycle-complete="nextRepetition"
              @phase-change="handlePhaseChange"
            />

            <!-- 进度动画组件 -->
            <ProgressAnimation
              :percentage="exerciseStore.exerciseProgress"
              :current-step="exerciseStore.currentRepetition"
              :total-steps="settingsStore.settings.repetitions"
              :show-linear="true"
              :show-steps="true"
              step-label="次"
              :is-animating="exerciseStore.isExercising"
              @complete="handleExerciseComplete"
              @step-change="handleStepChange"
            />

            <div class="time-display">
              <span>{{ formatTime(exerciseTime) }}</span>
            </div>

            <!-- 控制按钮 -->
            <div class="exercise-controls">
              <el-button @click="nextRepetition" type="primary" size="large">
                <el-icon><Check /></el-icon>
                完成一次
              </el-button>
              <el-button @click="stopExercise" type="danger" plain>
                <el-icon><Close /></el-icon>
                停止运动
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- 今日统计 -->
        <el-card class="stats-card">
          <template #header>
            <span>今日统计</span>
          </template>
          <div class="today-stats">
            <div class="stat-item">
              <el-icon class="stat-icon"><Trophy /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ exerciseStore.stats.todayCount }}</div>
                <div class="stat-label">完成次数</div>
              </div>
            </div>
            <div class="stat-item">
              <el-icon class="stat-icon"><Clock /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ exerciseStore.stats.streakDays }}</div>
                <div class="stat-label">连续天数</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-main>
    </el-container>

    <!-- 奖励动画 -->
    <RewardAnimation
      :visible="showReward"
      :reward-type="rewardType"
      :title="rewardTitle"
      :message="rewardMessage"
      :points="rewardPoints"
      :stats="rewardStats || undefined"
      @close="handleRewardClose"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSettingsStore } from '@/stores/settings'
import { useExerciseStore } from '@/stores/exercise'
import { ElMessage } from 'element-plus'
import BreathingAnimation from '@/components/BreathingAnimation.vue'
import ProgressAnimation from '@/components/ProgressAnimation.vue'
import RewardAnimation from '@/components/RewardAnimation.vue'

const router = useRouter()
const settingsStore = useSettingsStore()
const exerciseStore = useExerciseStore()

// 响应式数据
const exerciseTime = ref(0)
const isInhaling = ref(true)
const breathingTimer = ref<number | null>(null)
const exerciseTimer = ref<number | null>(null)

// 奖励动画相关
const showReward = ref(false)
const rewardType = ref<'success' | 'achievement' | 'milestone' | 'streak'>('success')
const rewardTitle = ref('恭喜！')
const rewardMessage = ref('你完成了一次运动！')
const rewardPoints = ref(0)
const rewardStats = ref<Record<string, { value: string | number; label: string }> | null>(null)

// 计算属性
const formatTime = computed(() => {
  return (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
})

// 方法
const startExercise = async () => {
  try {
    const success = await exerciseStore.beginExercise(
      settingsStore.settings.exerciseDuration,
      settingsStore.settings.repetitions
    )
    
    if (success) {
      startBreathingAnimation()
      startExerciseTimer()
      ElMessage.success('运动开始！')
    } else {
      ElMessage.error('开始运动失败')
    }
  } catch (error) {
    ElMessage.error('开始运动时出错')
  }
}

const stopExercise = async () => {
  try {
    await exerciseStore.finishExercise(false)
    stopAllTimers()
    ElMessage.info('运动已停止')
  } catch (error) {
    ElMessage.error('停止运动时出错')
  }
}

const nextRepetition = () => {
  exerciseStore.incrementRepetition()
  
  if (exerciseStore.currentRepetition >= settingsStore.settings.repetitions) {
    completeExercise()
  }
}

const completeExercise = async () => {
  try {
    await exerciseStore.finishExercise(true)
    stopAllTimers()
    showRewardAnimation()
  } catch (error) {
    ElMessage.error('完成运动时出错')
  }
}

// 动画相关方法
const handlePhaseChange = (phase: 'inhale' | 'exhale') => {
  isInhaling.value = phase === 'inhale'
}

const handleExerciseComplete = () => {
  completeExercise()
}

const handleStepChange = (step: number) => {
  // 可以在这里添加步骤变化的逻辑
  console.log('步骤变化:', step)
}

const showRewardAnimation = () => {
  // 根据完成情况设置不同的奖励类型
  const todayCount = exerciseStore.stats.todayCount + 1
  const streakDays = exerciseStore.stats.streakDays

  if (streakDays >= 30) {
    rewardType.value = 'milestone'
    rewardTitle.value = '里程碑达成！'
    rewardMessage.value = '连续运动30天，你是真正的健康达人！'
    rewardPoints.value = 100
  } else if (streakDays >= 7) {
    rewardType.value = 'streak'
    rewardTitle.value = '连续记录！'
    rewardMessage.value = `连续运动${streakDays}天，坚持就是胜利！`
    rewardPoints.value = 50
  } else if (todayCount >= 10) {
    rewardType.value = 'achievement'
    rewardTitle.value = '今日达人！'
    rewardMessage.value = '今天已完成10次运动，表现优秀！'
    rewardPoints.value = 30
  } else {
    rewardType.value = 'success'
    rewardTitle.value = '运动完成！'
    rewardMessage.value = '又完成了一次健康运动，继续保持！'
    rewardPoints.value = 10
  }

  rewardStats.value = {
    today: { value: todayCount, label: '今日次数' },
    streak: { value: streakDays, label: '连续天数' },
    total: { value: exerciseStore.stats.totalCount + 1, label: '总计次数' }
  }

  showReward.value = true
}

const handleRewardClose = () => {
  showReward.value = false
  ElMessage.success('恭喜！运动完成！')
}

const startBreathingAnimation = () => {
  // 呼吸节奏：4秒吸气，4秒呼气
  breathingTimer.value = setInterval(() => {
    isInhaling.value = !isInhaling.value
  }, 4000)
}

const startExerciseTimer = () => {
  exerciseTimer.value = setInterval(() => {
    exerciseTime.value++
  }, 1000)
}

const stopAllTimers = () => {
  if (breathingTimer.value) {
    clearInterval(breathingTimer.value)
    breathingTimer.value = null
  }
  
  if (exerciseTimer.value) {
    clearInterval(exerciseTimer.value)
    exerciseTimer.value = null
  }
  
  exerciseTime.value = 0
  isInhaling.value = true
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    settingsStore.loadSettings(),
    exerciseStore.loadStats()
  ])
})

onUnmounted(() => {
  stopAllTimers()
})
</script>

<style scoped>
.exercise-view {
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

.exercise-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: none;
  border-radius: 16px;
  margin-bottom: 20px;
}

.exercise-ready {
  text-align: center;
  padding: 20px;
}

.exercise-info h3 {
  color: #333;
  margin-bottom: 20px;
}

.exercise-params {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 30px;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 16px;
}

.exercise-guide {
  text-align: left;
  max-width: 400px;
  margin: 0 auto 30px;
}

.exercise-guide h4 {
  color: #333;
  margin-bottom: 15px;
}

.guide-steps {
  color: #666;
  line-height: 1.6;
}

.guide-steps li {
  margin-bottom: 8px;
}

.start-btn {
  font-size: 18px;
  padding: 15px 40px;
  border-radius: 25px;
}

.exercise-active {
  text-align: center;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.time-display {
  margin-top: 15px;
  font-size: 24px;
  font-weight: bold;
  color: #67c23a;
}

.exercise-controls {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.stats-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: none;
  border-radius: 16px;
}

.today-stats {
  display: flex;
  justify-content: space-around;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 32px;
  color: #67c23a;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #666;
}
</style>
