<template>
  <div class="stats-view">
    <el-container>
      <!-- 头部 -->
      <el-header class="header">
        <div class="header-content">
          <el-button @click="$router.back()" type="text" class="back-btn">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <h2>统计数据</h2>
          <el-button @click="refreshStats" type="text" class="refresh-btn">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </el-header>

      <!-- 主要内容 -->
      <el-main class="main-content">
        <!-- 概览统计 -->
        <div class="overview-stats">
          <el-card class="stat-card today">
            <div class="stat-content">
              <el-icon class="stat-icon"><Calendar /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ exerciseStore.stats.todayCount }}</div>
                <div class="stat-label">今日次数</div>
              </div>
            </div>
          </el-card>

          <el-card class="stat-card week">
            <div class="stat-content">
              <el-icon class="stat-icon"><DataLine /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ exerciseStore.stats.weekCount }}</div>
                <div class="stat-label">本周次数</div>
              </div>
            </div>
          </el-card>

          <el-card class="stat-card month">
            <div class="stat-content">
              <el-icon class="stat-icon"><TrendCharts /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ exerciseStore.stats.monthCount }}</div>
                <div class="stat-label">本月次数</div>
              </div>
            </div>
          </el-card>

          <el-card class="stat-card total">
            <div class="stat-content">
              <el-icon class="stat-icon"><Trophy /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ exerciseStore.stats.totalCount }}</div>
                <div class="stat-label">总计次数</div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 连续天数 -->
        <el-card class="streak-card">
          <template #header>
            <div class="card-header">
              <el-icon><Medal /></el-icon>
              <span>连续记录</span>
            </div>
          </template>
          <div class="streak-content">
            <div class="streak-number">{{ exerciseStore.stats.streakDays }}</div>
            <div class="streak-text">连续运动天数</div>
            <div class="streak-encouragement">
              {{ getEncouragementText(exerciseStore.stats.streakDays) }}
            </div>
          </div>
        </el-card>

        <!-- 图表区域 -->
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>运动趋势</span>
              <el-radio-group v-model="chartPeriod" size="small">
                <el-radio-button label="week">本周</el-radio-button>
                <el-radio-button label="month">本月</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container">
            <!-- 这里可以集成图表库，如ECharts -->
            <div class="chart-placeholder">
              <el-icon class="chart-icon"><TrendCharts /></el-icon>
              <p>图表功能开发中...</p>
              <p class="chart-desc">将显示{{ chartPeriod === 'week' ? '本周' : '本月' }}的运动趋势</p>
            </div>
          </div>
        </el-card>

        <!-- 成就系统 -->
        <el-card class="achievement-card">
          <template #header>
            <div class="card-header">
              <el-icon><Star /></el-icon>
              <span>成就系统</span>
            </div>
          </template>
          <div class="achievements">
            <div 
              v-for="achievement in achievements" 
              :key="achievement.id"
              class="achievement-item"
              :class="{ 'unlocked': achievement.unlocked }"
            >
              <el-icon class="achievement-icon">
                <component :is="achievement.icon" />
              </el-icon>
              <div class="achievement-info">
                <div class="achievement-title">{{ achievement.title }}</div>
                <div class="achievement-desc">{{ achievement.description }}</div>
                <div v-if="!achievement.unlocked" class="achievement-progress">
                  {{ achievement.current }}/{{ achievement.target }}
                </div>
              </div>
              <el-icon v-if="achievement.unlocked" class="achievement-check">
                <Check />
              </el-icon>
            </div>
          </div>
        </el-card>

        <!-- 最近记录 -->
        <el-card class="recent-card">
          <template #header>
            <div class="card-header">
              <el-icon><Clock /></el-icon>
              <span>最近记录</span>
            </div>
          </template>
          <div class="recent-records">
            <div v-if="exerciseStore.stats.lastExerciseTime" class="last-exercise">
              <p>最后运动时间：{{ formatLastExerciseTime }}</p>
            </div>
            <div v-else class="no-records">
              <el-icon><DocumentRemove /></el-icon>
              <p>暂无运动记录</p>
            </div>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useExerciseStore } from '@/stores/exercise'
import { ElMessage } from 'element-plus'

const router = useRouter()
const exerciseStore = useExerciseStore()

// 响应式数据
const chartPeriod = ref<'week' | 'month'>('week')

// 成就数据
const achievements = ref([
  {
    id: 1,
    title: '初学者',
    description: '完成第一次运动',
    icon: 'Trophy',
    target: 1,
    current: exerciseStore.stats.totalCount,
    unlocked: exerciseStore.stats.totalCount >= 1
  },
  {
    id: 2,
    title: '坚持者',
    description: '连续运动7天',
    icon: 'Medal',
    target: 7,
    current: exerciseStore.stats.streakDays,
    unlocked: exerciseStore.stats.streakDays >= 7
  },
  {
    id: 3,
    title: '百次达人',
    description: '累计完成100次运动',
    icon: 'Star',
    target: 100,
    current: exerciseStore.stats.totalCount,
    unlocked: exerciseStore.stats.totalCount >= 100
  },
  {
    id: 4,
    title: '月度冠军',
    description: '单月完成50次运动',
    icon: 'Crown',
    target: 50,
    current: exerciseStore.stats.monthCount,
    unlocked: exerciseStore.stats.monthCount >= 50
  }
])

// 计算属性
const formatLastExerciseTime = computed(() => {
  if (!exerciseStore.stats.lastExerciseTime) return ''
  
  const lastTime = new Date(exerciseStore.stats.lastExerciseTime)
  const now = new Date()
  const diffMs = now.getTime() - lastTime.getTime()
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffDays > 0) {
    return `${diffDays}天前`
  } else if (diffHours > 0) {
    return `${diffHours}小时前`
  } else {
    return '刚刚'
  }
})

// 方法
const getEncouragementText = (streakDays: number): string => {
  if (streakDays === 0) {
    return '开始你的健康之旅吧！'
  } else if (streakDays < 7) {
    return '很好的开始，继续保持！'
  } else if (streakDays < 30) {
    return '习惯正在养成，加油！'
  } else if (streakDays < 100) {
    return '你已经是运动达人了！'
  } else {
    return '健康大师，令人敬佩！'
  }
}

const refreshStats = async () => {
  try {
    await exerciseStore.loadStats()
    
    // 更新成就状态
    achievements.value.forEach(achievement => {
      if (achievement.id === 1 || achievement.id === 3) {
        achievement.current = exerciseStore.stats.totalCount
        achievement.unlocked = achievement.current >= achievement.target
      } else if (achievement.id === 2) {
        achievement.current = exerciseStore.stats.streakDays
        achievement.unlocked = achievement.current >= achievement.target
      } else if (achievement.id === 4) {
        achievement.current = exerciseStore.stats.monthCount
        achievement.unlocked = achievement.current >= achievement.target
      }
    })
    
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新数据失败')
  }
}

// 生命周期
onMounted(async () => {
  await refreshStats()
})
</script>

<style scoped>
.stats-view {
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
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
}

.header-content h2 {
  color: white;
  margin: 0;
}

.back-btn, .refresh-btn {
  color: white !important;
  font-size: 16px;
}

.main-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: none;
  border-radius: 16px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px;
}

.stat-icon {
  font-size: 32px;
  padding: 10px;
  border-radius: 8px;
}

.stat-card.today .stat-icon {
  background: #e3f2fd;
  color: #1976d2;
}

.stat-card.week .stat-icon {
  background: #f3e5f5;
  color: #7b1fa2;
}

.stat-card.month .stat-icon {
  background: #e8f5e8;
  color: #388e3c;
}

.stat-card.total .stat-icon {
  background: #fff3e0;
  color: #f57c00;
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

.streak-card, .chart-card, .achievement-card, .recent-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: none;
  border-radius: 16px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  color: #333;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.streak-content {
  text-align: center;
  padding: 20px;
}

.streak-number {
  font-size: 48px;
  font-weight: bold;
  color: #67c23a;
  margin-bottom: 10px;
}

.streak-text {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
}

.streak-encouragement {
  font-size: 14px;
  color: #666;
  font-style: italic;
}

.chart-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  text-align: center;
  color: #999;
}

.chart-icon {
  font-size: 64px;
  margin-bottom: 15px;
}

.chart-desc {
  font-size: 12px;
  margin-top: 10px;
}

.achievements {
  display: grid;
  gap: 15px;
}

.achievement-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border-radius: 8px;
  background: #f8f9fa;
  opacity: 0.6;
  transition: all 0.3s ease;
}

.achievement-item.unlocked {
  opacity: 1;
  background: linear-gradient(45deg, #fff3cd, #d1ecf1);
}

.achievement-icon {
  font-size: 24px;
  color: #666;
}

.achievement-item.unlocked .achievement-icon {
  color: #67c23a;
}

.achievement-info {
  flex: 1;
}

.achievement-title {
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.achievement-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.achievement-progress {
  font-size: 12px;
  color: #999;
}

.achievement-check {
  font-size: 20px;
  color: #67c23a;
}

.recent-records {
  padding: 20px;
  text-align: center;
}

.last-exercise p {
  color: #666;
  margin: 0;
}

.no-records {
  color: #999;
}

.no-records .el-icon {
  font-size: 32px;
  margin-bottom: 10px;
}
</style>
