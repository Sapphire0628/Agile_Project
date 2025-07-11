<template>
    <v-app-bar elevation="1">
      <v-app-bar-nav-icon @click="goHome">
        <v-icon 
          size="large" 
        >
          mdi-home
        </v-icon>
      </v-app-bar-nav-icon>

      <v-menu
        min-width="220"
        rounded="lg"
        offset="5"
      >
        <template v-slot:activator="{ props }">
          <v-btn
            v-bind="props"
            variant="text"
            class="project-selector"
          >
            <v-icon class="mr-2">mdi-briefcase</v-icon>
            Projects
          </v-btn>
        </template>
  
        <v-list class="pa-2" nav>
          <v-list-item
            v-for="project in allProjects"
            :key="project.project_id"
            @click="handleProjectChange(project.project_id)"
            rounded="lg"
            class="mb-1"
          >
            <template v-slot:prepend>
              <v-avatar
                size="32"
                :color="getProjectColor(project.project_name)"
              >
                <span class="text-caption font-weight-medium white--text">
                  {{ getProjectInitial(project.project_name) }}
                </span>
              </v-avatar>
            </template>
            <v-list-item-title class="text-body-2">{{ project.project_name }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
  
      <v-spacer></v-spacer>
  
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
            <v-list-item-title>Log out</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
  import router from '@/router/router.js'
  import { useStore } from 'vuex'
  import { getProjects } from '@/api/project'

  const store = useStore()
  const username = ref('')
  const userAvatar = ref('')
  const lastFetchTime = ref(0)
  const REFRESH_INTERVAL = 5 * 60 * 1000  
  let refreshTimer = null


  const fetchProjects = async () => {
    try {
      const now = Date.now()
      if (now - lastFetchTime.value < REFRESH_INTERVAL) {
        return
      }
      
      const response = await getProjects()
      store.commit('project/SET_WORKING_PROJECTS', response.data.project_belong)
      store.commit('project/SET_OWNED_PROJECTS', response.data.own_project)
      lastFetchTime.value = now
    } catch (error) {
      console.error('获取项目列表失败:', error)
    }
  }

  const handleRouteChange = async (to) => {
    if (to.path.includes('/project/')) {
      await fetchProjects()
    }
  }

  onMounted(() => {
    username.value = localStorage.getItem('username') || 'USER'
    userAvatar.value = localStorage.getItem('userAvatar') || ''
    fetchProjects()
    
    refreshTimer = setInterval(fetchProjects, REFRESH_INTERVAL)
    
    router.beforeEach(handleRouteChange)
  })

  onBeforeUnmount(() => {
    if (refreshTimer) {
      clearInterval(refreshTimer)
    }
    router.beforeEach(() => {})
  })

 
  const allProjects = computed(() => {
    const ownedProjects = store.getters['project/getOwnedProjects'] || []
    const workingProjects = store.getters['project/getWorkingProjects'] || []
    return [...ownedProjects, ...workingProjects]
  })

  const userInitials = computed(() => {
    return username.value
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .substring(0, 2)
  })
  
  const avatarColor = computed(() => {

    const colors = [
      '#2196F3', 
      '#4CAF50', 
      '#FF9800', 
      '#E91E63', 
      '#9C27B0',
      '#00BCD4', 
      '#009688', 
      '#F44336'  
    ]
    
    const hash = username.value.split('').reduce((acc, char) => {
      return char.charCodeAt(0) + ((acc << 5) - acc)
    }, 0)
    
    return colors[Math.abs(hash) % colors.length]
  })
  

  const goHome = () => {
    router.push('/home')
  }
  

  const handleProjectChange = (projectId) => {
    router.push(`/project/${projectId}`)
  }
  
  const handleLogout = () => {
    try {
      store.dispatch('user/logout')
      router.push('/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }


  const getProjectInitial = (projectName) => {
    return projectName ? projectName.charAt(0).toUpperCase() : 'P'
  }


  const getProjectColor = (projectName) => {
    const colors = [
      'rgb(25, 118, 210)',   
      'rgb(56, 142, 60)',    
      'rgb(211, 47, 47)',    
      'rgb(123, 31, 162)',   
      'rgb(245, 124, 0)',    
      'rgb(0, 151, 167)'     
    ]
  
    const project = allProjects.value.find(p => p.project_name === projectName)
    if (!project) return colors[0]
    
    return colors[project.project_id % colors.length]
  }
  </script>
  
  <style scoped>
  .cursor-pointer {
    cursor: pointer;
  }
  

  .v-avatar span {
    color: white;
  }

  .project-selector {
    min-width: 100px;
    justify-content: flex-start;
  }

  :deep(.v-list-item--active) {
    background-color: rgb(var(--v-theme-primary), 0.1);
  }

  :deep(.v-list-item:hover) {
    background-color: rgb(var(--v-theme-surface-variant));
  }

  :deep(.v-list-subheader) {
    padding-inline: 16px;
  }
  </style>