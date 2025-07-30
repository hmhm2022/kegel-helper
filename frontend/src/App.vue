<template>
  <div id="app">
    <router-view />

    <!-- 桌面应用标题栏已移除，使用默认标题栏 -->
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

// 应用初始化
onMounted(async () => {
  // 应用已经是自包含的，无需额外初始化
  console.log('应用已启动')
})
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100vh;
  margin: 0;
  padding: 0;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
}
</style>
