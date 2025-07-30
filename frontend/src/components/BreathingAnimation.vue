<template>
  <div class="breathing-animation">
    <div class="animation-container">
      <!-- 主呼吸圆圈 -->
      <div 
        class="breathing-circle main-circle"
        :class="{ 
          'inhale': isInhaling, 
          'exhale': !isInhaling,
          'active': isActive 
        }"
      >
        <!-- 内部装饰圆圈 -->
        <div class="inner-circle"></div>
        <div class="center-dot"></div>
      </div>

      <!-- 外围装饰圆环 -->
      <div 
        class="outer-ring"
        :class="{ 'active': isActive }"
      ></div>

      <!-- 粒子效果 -->
      <div class="particles" v-if="isActive">
        <div 
          v-for="i in 8" 
          :key="i" 
          class="particle"
          :style="{ '--delay': i * 0.5 + 's' }"
        ></div>
      </div>
    </div>

    <!-- 呼吸指导文字 -->
    <div class="breathing-text">
      <div class="phase-text" :class="{ 'inhale': isInhaling, 'exhale': !isInhaling }">
        {{ isInhaling ? '吸气 - 收缩' : '呼气 - 放松' }}
      </div>
      <div class="instruction-text">
        {{ isInhaling ? '慢慢收紧肛门肌肉' : '缓缓放松肌肉' }}
      </div>
    </div>

    <!-- 进度指示器 -->
    <div class="progress-indicator" v-if="showProgress">
      <div class="progress-dots">
        <div 
          v-for="i in totalCycles" 
          :key="i"
          class="progress-dot"
          :class="{ 'completed': i <= currentCycle }"
        ></div>
      </div>
      <div class="cycle-text">
        {{ currentCycle }}/{{ totalCycles }} 次
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'

// Props
interface Props {
  isActive?: boolean
  cycleDuration?: number // 一个完整呼吸周期的时长（秒）
  showProgress?: boolean
  totalCycles?: number
  currentCycle?: number
}

const props = withDefaults(defineProps<Props>(), {
  isActive: false,
  cycleDuration: 8, // 4秒吸气 + 4秒呼气
  showProgress: false,
  totalCycles: 10,
  currentCycle: 0
})

// Emits
const emit = defineEmits<{
  cycleComplete: []
  phaseChange: [phase: 'inhale' | 'exhale']
}>()

// 响应式数据
const isInhaling = ref(true)
const animationTimer = ref<number | null>(null)

// 方法
const startAnimation = () => {
  if (animationTimer.value) {
    clearInterval(animationTimer.value)
  }

  // 每半个周期切换一次呼吸阶段
  const phaseInterval = (props.cycleDuration * 1000) / 2

  animationTimer.value = setInterval(() => {
    isInhaling.value = !isInhaling.value
    emit('phaseChange', isInhaling.value ? 'inhale' : 'exhale')
    
    // 如果从呼气切换到吸气，表示完成了一个完整周期
    if (isInhaling.value) {
      emit('cycleComplete')
    }
  }, phaseInterval)
}

const stopAnimation = () => {
  if (animationTimer.value) {
    clearInterval(animationTimer.value)
    animationTimer.value = null
  }
  isInhaling.value = true // 重置到初始状态
}

// 监听激活状态
watch(() => props.isActive, (newValue) => {
  if (newValue) {
    startAnimation()
  } else {
    stopAnimation()
  }
})

// 生命周期
onMounted(() => {
  if (props.isActive) {
    startAnimation()
  }
})

onUnmounted(() => {
  stopAnimation()
})

// 暴露方法给父组件
defineExpose({
  startAnimation,
  stopAnimation
})
</script>

<style scoped>
.breathing-animation {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
  padding: 20px;
}

.animation-container {
  position: relative;
  width: 200px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.breathing-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(45deg, #67c23a, #85ce61);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: transform 4s cubic-bezier(0.4, 0, 0.6, 1);
  box-shadow: 
    0 0 20px rgba(103, 194, 58, 0.3),
    inset 0 0 20px rgba(255, 255, 255, 0.2);
}

.breathing-circle.active.inhale {
  transform: scale(1.3);
  box-shadow: 
    0 0 40px rgba(103, 194, 58, 0.6),
    inset 0 0 20px rgba(255, 255, 255, 0.3);
}

.breathing-circle.active.exhale {
  transform: scale(0.9);
  box-shadow: 
    0 0 15px rgba(103, 194, 58, 0.2),
    inset 0 0 15px rgba(255, 255, 255, 0.1);
}

.inner-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.center-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.outer-ring {
  position: absolute;
  width: 160px;
  height: 160px;
  border: 2px solid rgba(103, 194, 58, 0.3);
  border-radius: 50%;
  animation: rotate 20s linear infinite;
}

.outer-ring.active {
  border-color: rgba(103, 194, 58, 0.6);
  box-shadow: 0 0 20px rgba(103, 194, 58, 0.3);
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.particles {
  position: absolute;
  width: 100%;
  height: 100%;
}

.particle {
  position: absolute;
  width: 6px;
  height: 6px;
  background: #67c23a;
  border-radius: 50%;
  opacity: 0;
  animation: particle-float 4s ease-in-out infinite;
  animation-delay: var(--delay);
}

.particle:nth-child(1) { top: 0; left: 50%; transform: translateX(-50%); }
.particle:nth-child(2) { top: 15%; right: 15%; }
.particle:nth-child(3) { top: 50%; right: 0; transform: translateY(-50%); }
.particle:nth-child(4) { bottom: 15%; right: 15%; }
.particle:nth-child(5) { bottom: 0; left: 50%; transform: translateX(-50%); }
.particle:nth-child(6) { bottom: 15%; left: 15%; }
.particle:nth-child(7) { top: 50%; left: 0; transform: translateY(-50%); }
.particle:nth-child(8) { top: 15%; left: 15%; }

@keyframes particle-float {
  0%, 100% { 
    opacity: 0; 
    transform: scale(0.5) translateY(0); 
  }
  50% { 
    opacity: 1; 
    transform: scale(1) translateY(-10px); 
  }
}

.breathing-text {
  text-align: center;
}

.phase-text {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
  transition: color 0.5s ease;
}

.phase-text.inhale {
  color: #67c23a;
}

.phase-text.exhale {
  color: #409eff;
}

.instruction-text {
  font-size: 16px;
  color: #666;
  font-style: italic;
}

.progress-indicator {
  text-align: center;
}

.progress-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 10px;
}

.progress-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e4e7ed;
  transition: background-color 0.3s ease;
}

.progress-dot.completed {
  background: #67c23a;
  box-shadow: 0 0 8px rgba(103, 194, 58, 0.5);
}

.cycle-text {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .animation-container {
    width: 160px;
    height: 160px;
  }
  
  .breathing-circle {
    width: 100px;
    height: 100px;
  }
  
  .inner-circle {
    width: 65px;
    height: 65px;
  }
  
  .center-dot {
    width: 16px;
    height: 16px;
  }
  
  .outer-ring {
    width: 130px;
    height: 130px;
  }
  
  .phase-text {
    font-size: 20px;
  }
  
  .instruction-text {
    font-size: 14px;
  }
}
</style>
