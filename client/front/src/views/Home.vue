<template>
  <v-layout class="home">
    <Header />
    
    <v-container>
      <h1 class="text-h4 text-primary mb-6">Projects Dashboard</h1>
      
      <v-row>
        <v-col cols="12" md="6">
          <!-- 管理的项目 -->
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
          <!-- 所属的项目 -->
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

      <!-- 管理项目按钮 -->
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
</template>

<script>
import { computed, onMounted } from 'vue'
import Header from '@/components/Header.vue'
import ProjectCard from '@/components/ProjectCard.vue'
import { getProjects } from '@/api/project'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'Home',
  components: {
    Header,
    ProjectCard
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const workingProjects = computed(() => store.getters['project/getWorkingProjects'])
    const ownedProjects = computed(() => store.getters['project/getOwnedProjects'])
    const fetchProjects = async () => {
      try {
        const response = await getProjects()
        const workingProjects = response.data.project_belong
        const ownedProjects = response.data.own_project
        store.commit('project/SET_WORKING_PROJECTS', workingProjects)
        store.commit('project/SET_OWNED_PROJECTS', ownedProjects)
      } catch (err) {
        console.error('获取项目失败:', err)
      }
    }
    const handleProjectDeleted = (projectId) => {
      store.commit('project/REMOVE_PROJECT', projectId)
    }
    const goToManageProjects = () => {
      router.push('/add-project')
    }

    // 组件挂载时获取数据
    onMounted(() => {
        fetchProjects()
    })
    return {
      workingProjects,
      ownedProjects,
      fetchProjects,
      goToManageProjects,
      handleProjectDeleted
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
</style>
