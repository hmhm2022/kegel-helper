<template>
  <div class="progress-animation">
    <!-- 圆形进度条 -->
    <div class="circular-progress">
      <svg class="progress-svg" :width="size" :height="size">
        <!-- 背景圆环 -->
        <circle
          class="progress-bg"
          :cx="center"
          :cy="center"
          :r="radius"
          fill="none"
          :stroke-width="strokeWidth"
        />
        <!-- 进度圆环 -->
        <circle
          class="progress-bar"
          :cx="center"
          :cy="center"
          :r="radius"
          fill="none"
          :stroke-width="strokeWidth"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="strokeDashoffset"
          :style="{ '--duration': animationDuration + 's' }"
        />
      </svg>
      
      <!-- 中心内容 -->
      <div class="progress-content">
        <div class="progress-value">{{ Math.round(percentage) }}%</div>
        <div class="progress-label">{{ label }}</div>
      </div>
    </div>

    <!-- 线性进度条（可选） -->
    <div v-if="showLinear" class="linear-progress">
      <div class="linear-bg">
        <div 
          class="linear-bar"
          :style="{ 
            width: percentage + '%',
            '--duration': animationDuration + 's'
          }"
        ></div>
      </div>
      <div class="linear-text">
        {{ currentStep }}/{{ totalSteps }} {{ stepLabel }}
      </div>
    </div>

    <!-- 步骤指示器 -->
    <div v-if="showSteps" class="step-indicators">
      <div 
        v-for="step in totalSteps" 
        :key="step"
        class="step-indicator"
        :class="{ 
          'completed': step <= currentStep,
          'active': step === currentStep + 1,
          'pulse': step === currentStep + 1 && isAnimating
        }"
      >
        <div class="step-number">{{ step }}</div>
        <div class="step-connector" v-if="step < totalSteps"></div>
      </div>
    </div>

    <!-- 成功动画 -->
    <div v-if="showSuccess" class="success-animation">
      <div class="success-circle">
        <el-icon class="success-icon"><Check /></el-icon>
      </div>
      <div class="success-text">{{ successText }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

// Props
interface Props {
  percentage: number
  size?: number
  strokeWidth?: number
  color?: string
  backgroundColor?: string
  label?: string
  showLinear?: boolean
  showSteps?: boolean
  showSuccess?: boolean
  currentStep?: number
  totalSteps?: number
  stepLabel?: string
  successText?: string
  animationDuration?: number
  isAnimating?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  percentage: 0,
  size: 120,
  strokeWidth: 8,
  color: '#67c23a',
  backgroundColor: '#e4e7ed',
  label: '进度',
  showLinear: false,
  showSteps: false,
  showSuccess: false,
  currentStep: 0,
  totalSteps: 10,
  stepLabel: '步骤',
  successText: '完成！',
  animationDuration: 0.5,
  isAnimating: false
})

// Emits
const emit = defineEmits<{
  complete: []
  stepChange: [step: number]
}>()

// 计算属性
const center = computed(() => props.size / 2)
const radius = computed(() => (props.size - props.strokeWidth) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)

const strokeDashoffset = computed(() => {
  const progress = Math.min(Math.max(props.percentage, 0), 100)
  return circumference.value - (progress / 100) * circumference.value
})

// 监听进度变化
watch(() => props.percentage, (newValue, oldValue) => {
  if (newValue >= 100 && oldValue < 100) {
    setTimeout(() => {
      emit('complete')
    }, props.animationDuration * 1000)
  }
})

watch(() => props.currentStep, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    emit('stepChange', newValue)
  }
})
</script>

<style scoped>
.progress-animation {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.circular-progress {
  position: relative;
  display: inline-block;
}

.progress-svg {
  transform: rotate(-90deg);
}

.progress-bg {
  stroke: v-bind(backgroundColor);
  opacity: 0.3;
}

.progress-bar {
  stroke: v-bind(color);
  stroke-linecap: round;
  transition: stroke-dashoffset var(--duration) ease-in-out;
  filter: drop-shadow(0 0 6px rgba(103, 194, 58, 0.3));
}

.progress-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.progress-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.progress-label {
  font-size: 12px;
  color: #666;
}

.linear-progress {
  width: 100%;
  max-width: 300px;
}

.linear-bg {
  width: 100%;
  height: 8px;
  background: v-bind(backgroundColor);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.linear-bar {
  height: 100%;
  background: linear-gradient(90deg, v-bind(color), #85ce61);
  border-radius: 4px;
  transition: width var(--duration) ease-in-out;
  position: relative;
}

.linear-bar::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 20px;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3));
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.linear-text {
  text-align: center;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.step-indicators {
  display: flex;
  align-items: center;
  gap: 0;
}

.step-indicator {
  display: flex;
  align-items: center;
  position: relative;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e4e7ed;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.3s ease;
  position: relative;
  z-index: 2;
}

.step-indicator.completed .step-number {
  background: v-bind(color);
  color: white;
  box-shadow: 0 0 10px rgba(103, 194, 58, 0.3);
}

.step-indicator.active .step-number {
  background: #409eff;
  color: white;
  box-shadow: 0 0 10px rgba(64, 158, 255, 0.3);
}

.step-indicator.pulse .step-number {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.step-connector {
  width: 40px;
  height: 2px;
  background: #e4e7ed;
  margin: 0 -1px;
  transition: background-color 0.3s ease;
  position: relative;
  z-index: 1;
}

.step-indicator.completed .step-connector {
  background: v-bind(color);
}

.success-animation {
  text-align: center;
  animation: success-appear 0.5s ease-out;
}

@keyframes success-appear {
  0% {
    opacity: 0;
    transform: scale(0.5);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.success-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #67c23a;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  box-shadow: 0 0 20px rgba(103, 194, 58, 0.4);
  animation: success-bounce 0.6s ease-out;
}

@keyframes success-bounce {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.success-icon {
  font-size: 24px;
  color: white;
}

.success-text {
  font-size: 18px;
  font-weight: bold;
  color: #67c23a;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .progress-value {
    font-size: 16px;
  }
  
  .progress-label {
    font-size: 11px;
  }
  
  .step-number {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }
  
  .step-connector {
    width: 30px;
  }
  
  .success-circle {
    width: 50px;
    height: 50px;
  }
  
  .success-icon {
    font-size: 20px;
  }
  
  .success-text {
    font-size: 16px;
  }
}
</style>
