<template>
  <v-layout class="home">
    <Header />
    
    <v-container>
      <h1 class="text-h4 text-primary mb-6">Projects Dashboard</h1>
      
      <v-row>
        <v-col cols="12" md="6">
          <v-card class="pa-4">
            <h2 class="text-h6 mb-4">Owned</h2>
            <div class="project-list">
              <div class="projects-container">
                <ProjectCard 
                  v-for="project in ownedProjects" 
                  :key="project.project_id"
                  :project="project"
                  @project-deleted="handleProjectDeleted"
                />
              </div>
            </div>
          </v-card>
        </v-col>
        <v-col cols="12" md="6">
          <v-card class="pa-4">
            <h2 class="text-h6 mb-4">Belong to</h2>
            <div class="project-list">
              <div class="projects-container">
                <ProjectCard 
                  v-for="project in workingProjects" 
                  :key="project.project_id"
                  :project="project"
                  @project-deleted="handleProjectDeleted"
                />
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>

      <h2 class="text-h4 text-primary mb-6 mt-8">My Tasks</h2>
      <v-card class="pa-4">
        <div class="tasks-container">
          <v-list v-if="tasks.length > 0">
            <v-list-item
              v-for="task in tasks"
              :key="task.task_id"
              :value="task"
              class="mb-2 task-item"
              rounded="lg"
              @click="openTaskCard(task)"
            >
              <template v-slot:prepend>
                <v-avatar
                  size="40"
                  :color="getStatusColor(task.status)"
                  class="mr-3"
                >
                  <v-icon color="white">
                    {{ getStatusIcon(task.status) }}
                  </v-icon>
                </v-avatar>
              </template>

              <v-list-item-title class="text-h6 mb-1">
                {{ task.task_name }}
              </v-list-item-title>
              
              <v-list-item-subtitle>
                <div class="d-flex align-center mt-1">
                  <v-icon size="small" class="mr-1">mdi-folder-outline</v-icon>
                  <span class="text-caption mr-4">Project: {{ getProjectName(task.project_id) }}</span>
                  
                  <v-icon size="small" class="mr-1">mdi-calendar</v-icon>
                  <span class="text-caption">Due: {{ formatDate(task.due_date) }}</span>
                  <v-chip
                    size="small"
                    :color="getPriorityColor(task.priority)"
                    class="ml-4"
                    label
                  >
                    Story Points: {{ task.priority }}
                  </v-chip>
                </div>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
          <div v-else class="text-center pa-4">
            <v-icon size="40" color="grey">mdi-checkbox-blank-outline</v-icon>
            <p class="text-grey mt-2">No tasks assigned</p>
          </div>
        </div>
      </v-card>

      <div class="text-center mt-6">
        <v-btn
          color="cyan-lighten-3"
          size="large"
          @click="goToManageProjects"
          class="px-6"
        >
          Add Project
        </v-btn>
      </div>
    </v-container>
  </v-layout>
  <TaskCard
    v-model="showTaskCard"
    :task-id="selectedTaskId"
    :project-id="selectedProjectId"
    @task-updated="handleTaskUpdate"
  />
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import Header from '@/components/Header.vue'
import ProjectCard from '@/components/ProjectCard.vue'
import { getProjects } from '@/api/project'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import TaskCard from '@/components/TaskCard.vue'

export default {
  name: 'Home',
  components: {
    Header,
    ProjectCard,
    TaskCard
  },
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    const isLoading = ref(false)
    const workingProjects = computed(() => store.getters['project/getWorkingProjects'])
    const ownedProjects = computed(() => store.getters['project/getOwnedProjects'])
    const tasks = ref([])
    const showTaskCard = ref(false)
    const selectedTaskId = ref('')
    const selectedProjectId = ref('')

    const fetchData = async () => {
      if (isLoading.value) return
      isLoading.value = true

      try {
        const response = await getProjects()
        const { project_belong, own_project, tasks: tasksList } = response.data
        
        store.commit('project/SET_WORKING_PROJECTS', project_belong)
        store.commit('project/SET_OWNED_PROJECTS', own_project)
        tasks.value = tasksList
      } catch (err) {
        console.error('获取项目失败:', err)
      } finally {
        isLoading.value = false
      }
    }

    watch(
      () => route.path,
      (newPath) => {
        if (newPath === '/') {  
          fetchData()
        }
      }
    )

    onMounted(() => {
      fetchData()
    })

    const handleProjectDeleted = (projectId) => {
      store.commit('project/REMOVE_PROJECT', projectId)
    }
    const goToManageProjects = () => {
      router.push('/add-project')
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const getStatusColor = (status) => {
      const colors = {
        'Not start': 'grey',
        'Started': 'blue',
        'Testing': 'orange',
        'Review': 'purple',
        'Done': 'success'
      }
      return colors[status] || 'grey'
    }

    const getStatusIcon = (status) => {
      const icons = {
        'Not start': 'mdi-clock-outline',
        'Started': 'mdi-progress-clock',
        'Testing': 'mdi-test-tube',
        'Review': 'mdi-eye-outline',
        'Done': 'mdi-check-circle'
      }
      return icons[status] || 'mdi-help-circle'
    }

    const getPriorityColor = (priority) => {
      if (priority >= 13) return 'error'
      if (priority >= 7) return 'warning'
      return 'success'
    }

    const openTaskCard = (task) => {
      selectedTaskId.value = task.task_id
      selectedProjectId.value = task.project_id
      showTaskCard.value = true
    }

    const handleTaskUpdate = () => {
      fetchData()
    }

    const getProjectName = (projectId) => {
      const allProjects = [...workingProjects.value, ...ownedProjects.value]
      const project = allProjects.find(p => p.project_id === projectId)
      return project ? project.project_name : `Project ${projectId}`
    }

    return {
      workingProjects,
      ownedProjects,
      isLoading,
      fetchData,
      goToManageProjects,
      handleProjectDeleted,
      getStatusColor,
      getStatusIcon,
      getPriorityColor,
      openTaskCard,
      formatDate,
      tasks,
      showTaskCard,
      selectedTaskId,
      selectedProjectId,
      handleTaskUpdate,
      getProjectName
    }
  }
}
</script>

<style scoped>
.home {
  padding-bottom: 2rem;
  background-color: rgb(var(--v-theme-background));
}

.projects-container {
  max-height: 600px; 
  overflow-y: auto;
  padding-right: 8px; 
}

.projects-container::-webkit-scrollbar {
  width: 6px;
}

.projects-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.projects-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.projects-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.task-item {
  border: 1px solid rgba(var(--v-border-color), 0.12);
  transition: all 0.3s ease;
}

.tasks-container {
  max-height: 400px;
  overflow-y: auto;
}

.tasks-container::-webkit-scrollbar {
  width: 6px;
}

.tasks-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.tasks-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.tasks-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.v-list-item {
  border: 1px solid rgba(var(--v-border-color), 0.12);
  transition: all 0.3s ease;
}

.v-list-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>
