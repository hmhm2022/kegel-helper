<template>
  <div class="reward-animation" v-if="visible">
    <!-- 背景遮罩 -->
    <div class="reward-overlay" @click="close"></div>
    
    <!-- 奖励内容 -->
    <div class="reward-content" :class="{ 'show': showContent }">
      <!-- 庆祝粒子效果 -->
      <div class="confetti-container">
        <div 
          v-for="i in 50" 
          :key="i"
          class="confetti"
          :style="getConfettiStyle(i)"
        ></div>
      </div>

      <!-- 主要奖励图标 -->
      <div class="reward-icon-container">
        <div class="reward-icon" :class="rewardType">
          <el-icon>
            <component :is="getRewardIcon" />
          </el-icon>
        </div>
        <div class="reward-glow"></div>
      </div>

      <!-- 奖励文字 -->
      <div class="reward-text">
        <h2 class="reward-title">{{ title }}</h2>
        <p class="reward-message">{{ message }}</p>
        <div v-if="points" class="reward-points">
          +{{ points }} 积分
        </div>
      </div>

      <!-- 统计信息 -->
      <div v-if="stats" class="reward-stats">
        <div class="stat-item" v-for="(stat, key) in stats" :key="key">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>

      <!-- 关闭按钮 -->
      <el-button 
        type="primary" 
        size="large" 
        class="reward-close-btn"
        @click="close"
      >
        {{ closeText }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'

// Props
interface Props {
  visible: boolean
  rewardType?: 'success' | 'achievement' | 'milestone' | 'streak'
  title?: string
  message?: string
  points?: number
  stats?: Record<string, { value: string | number; label: string }>
  closeText?: string
  autoClose?: boolean
  autoCloseDelay?: number
}

const props = withDefaults(defineProps<Props>(), {
  rewardType: 'success',
  title: '恭喜！',
  message: '你完成了一次运动！',
  closeText: '继续',
  autoClose: false,
  autoCloseDelay: 3000
})

// Emits
const emit = defineEmits<{
  close: []
}>()

// 响应式数据
const showContent = ref(false)

// 计算属性
const getRewardIcon = computed(() => {
  const icons = {
    success: 'Check',
    achievement: 'Trophy',
    milestone: 'Medal',
    streak: 'Star'
  }
  return icons[props.rewardType] || 'Check'
})

// 方法
const getConfettiStyle = (index: number) => {
  const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3', '#54a0ff']
  const randomColor = colors[index % colors.length]
  const randomDelay = Math.random() * 3
  const randomDuration = 2 + Math.random() * 2
  const randomX = Math.random() * 100
  const randomRotation = Math.random() * 360
  
  return {
    '--color': randomColor,
    '--delay': randomDelay + 's',
    '--duration': randomDuration + 's',
    '--x': randomX + '%',
    '--rotation': randomRotation + 'deg'
  }
}

const close = () => {
  showContent.value = false
  setTimeout(() => {
    emit('close')
  }, 300)
}

// 生命周期
onMounted(async () => {
  if (props.visible) {
    await nextTick()
    setTimeout(() => {
      showContent.value = true
    }, 100)
    
    // 自动关闭
    if (props.autoClose) {
      setTimeout(() => {
        close()
      }, props.autoCloseDelay)
    }
  }
})
</script>

<style scoped>
.reward-animation {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reward-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  animation: overlay-appear 0.3s ease-out;
}

@keyframes overlay-appear {
  from { opacity: 0; }
  to { opacity: 1; }
}

.reward-content {
  position: relative;
  background: white;
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  transform: scale(0.5) translateY(50px);
  opacity: 0;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.reward-content.show {
  transform: scale(1) translateY(0);
  opacity: 1;
}

.confetti-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
  border-radius: 20px;
}

.confetti {
  position: absolute;
  width: 8px;
  height: 8px;
  background: var(--color);
  top: -10px;
  left: var(--x);
  animation: confetti-fall var(--duration) ease-in var(--delay) infinite;
  transform: rotate(var(--rotation));
}

.confetti:nth-child(odd) {
  border-radius: 50%;
}

.confetti:nth-child(even) {
  clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
}

@keyframes confetti-fall {
  0% {
    transform: translateY(-10px) rotate(var(--rotation));
    opacity: 1;
  }
  100% {
    transform: translateY(400px) rotate(calc(var(--rotation) + 180deg));
    opacity: 0;
  }
}

.reward-icon-container {
  position: relative;
  margin-bottom: 30px;
}

.reward-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  font-size: 36px;
  color: white;
  position: relative;
  z-index: 2;
  animation: icon-bounce 0.6s ease-out 0.2s both;
}

.reward-icon.success {
  background: linear-gradient(45deg, #67c23a, #85ce61);
}

.reward-icon.achievement {
  background: linear-gradient(45deg, #e6a23c, #f7ba2a);
}

.reward-icon.milestone {
  background: linear-gradient(45deg, #409eff, #66b1ff);
}

.reward-icon.streak {
  background: linear-gradient(45deg, #f56c6c, #f78989);
}

@keyframes icon-bounce {
  0% { transform: scale(0) rotate(-180deg); }
  50% { transform: scale(1.2) rotate(-90deg); }
  100% { transform: scale(1) rotate(0deg); }
}

.reward-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(103, 194, 58, 0.3), transparent);
  animation: glow-pulse 2s ease-in-out infinite;
  z-index: 1;
}

@keyframes glow-pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
  50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.8; }
}

.reward-text {
  margin-bottom: 30px;
}

.reward-title {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
  animation: text-slide-up 0.5s ease-out 0.4s both;
}

.reward-message {
  font-size: 16px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 15px;
  animation: text-slide-up 0.5s ease-out 0.5s both;
}

.reward-points {
  font-size: 20px;
  font-weight: bold;
  color: #67c23a;
  animation: text-slide-up 0.5s ease-out 0.6s both;
}

@keyframes text-slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.reward-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  animation: stats-appear 0.5s ease-out 0.7s both;
}

@keyframes stats-appear {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

.reward-close-btn {
  font-size: 16px;
  padding: 12px 30px;
  border-radius: 25px;
  animation: button-appear 0.5s ease-out 0.8s both;
}

@keyframes button-appear {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .reward-content {
    padding: 30px 20px;
    margin: 20px;
  }
  
  .reward-icon {
    width: 60px;
    height: 60px;
    font-size: 28px;
  }
  
  .reward-glow {
    width: 100px;
    height: 100px;
  }
  
  .reward-title {
    font-size: 24px;
  }
  
  .reward-message {
    font-size: 14px;
  }
  
  .reward-points {
    font-size: 18px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .reward-close-btn {
    font-size: 14px;
    padding: 10px 25px;
  }
}
</style>
