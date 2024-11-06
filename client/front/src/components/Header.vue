<template>
    <v-app-bar elevation="1">
      <!-- 返回主页的图标 -->
      <v-app-bar-nav-icon @click="goHome">
        <v-img
          src="@/assets/logo.png"
          max-height="40"
          max-width="40"
          contain
        ></v-img>
      </v-app-bar-nav-icon>
  
      <!-- 项目选择下拉菜单 -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            v-bind="props"
            variant="text"
          >
            {{ currentProject.name || '选择项目' }}
            <v-icon end>mdi-chevron-down</v-icon>
          </v-btn>
        </template>
  
        <v-list>
          <v-list-item
            v-for="project in projects"
            :key="project.id"
            @click="handleProjectChange(project.id)"
          >
            <v-list-item-title>{{ project.name }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
  
      <v-spacer></v-spacer>
  
      <!-- 用户头像和登出选项 -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-avatar
            v-bind="props"
            size="40"
            class="cursor-pointer"
            :color="avatarColor"
          >
            <span v-if="!userAvatar" class="text-h6 font-weight-medium">
              {{ userInitials }}
            </span>
            <v-img
              v-else
              :src="userAvatar"
              alt="用户头像"
            ></v-img>
          </v-avatar>
        </template>
  
        <v-list>
          <v-list-item @click="handleLogout">
            <v-list-item-title>登出</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import router from '@/router/router.js'
  
  const currentProject = ref({})
  const projects = ref([])
  const userAvatar = ref('')
  const username = ref('USER') // 这里替换为实际的用户名
  
  // 生成用户名首字母
  const userInitials = computed(() => {
    return username.value
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .substring(0, 2)
  })
  
  // 为头像生成随机颜色
  const avatarColor = computed(() => {
    // 使用用户名生成一个固定的颜色，这样每次刷新颜色都是一样的
    const colors = [
      '#2196F3', // 蓝色
      '#4CAF50', // 绿色
      '#FF9800', // 橙色
      '#E91E63', // 粉色
      '#9C27B0', // 紫色
      '#00BCD4', // 青色
      '#009688', // 蓝绿色
      '#F44336'  // 红色
    ]
    
    const hash = username.value.split('').reduce((acc, char) => {
      return char.charCodeAt(0) + ((acc << 5) - acc)
    }, 0)
    
    return colors[Math.abs(hash) % colors.length]
  })
  
  // 返回主页
  const goHome = () => {
    router.push('/home')
  }
  
  // 处理项目切换
  const handleProjectChange = (projectId) => {
    // 处理项目切换逻辑
  }
  
  // 处理登出
  const handleLogout = () => {
    // 处理登出逻辑
    // 清除用户token等信息
    localStorage.removeItem('token')
    router.push('/login')
  }
  </script>
  
  <style scoped>
  .cursor-pointer {
    cursor: pointer;
  }
  
  /* 确保头像中的文字是白色的 */
  .v-avatar span {
    color: white;
  }
  </style>