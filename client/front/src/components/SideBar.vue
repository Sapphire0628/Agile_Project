<template>
  <v-navigation-drawer
    permanent
    expand-on-hover
    width="200"
  >
    <v-list class="py-4">
      <v-list-item
        prepend-icon="mdi-arrow-left-circle"
        title="Backlog"
        value="project"
        :active="isProjectRoute"
        @click="navigateToProject"
      >
      </v-list-item>
      <v-list-item
        prepend-icon="mdi-account-group"
        title="Team"
        value="team"
        :active="isTeamRoute"
        @click="navigateToTeam"
      >
      </v-list-item>
      <v-list-group value="sprints"> 
        <template #activator="{ props }">
          <v-list-item
            v-bind="props"
            prepend-icon="mdi-run"
            title="Sprints"
          ></v-list-item>
        </template>
        <v-list-item v-for="sprint in sprints" 
          :key="sprint.id" 
          :title="sprint.name"
          @click="navigateToSprint(sprint.id, sprint.name)"
          prepend-icon="mdi-chevron-right"
        ></v-list-item>
      </v-list-group>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import { ref,computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSprints } from '@/api/sprint'


export default {
  expose: ['fetchSprints'],

  setup() {
    const route = useRoute()
    const router = useRouter()
    const sprints = ref([])

    const isTeamRoute = computed(() => {
      return route.name === 'Team'
    })

    const isProjectRoute = computed(() => {
      return route.name === 'Project'
    })

    const navigateToTeam = () => {
      const projectId = route.params.id
      router.push(`/project/${projectId}/team`)
    }

    const navigateToProject = () => {
      const projectId = route.params.id
      router.push(`/project/${projectId}`)
    }

    const navigateToSprint = (sprintId, sprintName) => {
      router.push(`/project/${route.params.id}/${sprintName}/${sprintId}`)
    }

    const fetchSprints = async () => {
      const response = await getSprints({ project_id: route.params.id })
      sprints.value = Object.keys(response.data).map(key => ({
        id: key,
        ...response.data[key],
        tasks: response.data[key].total_tasks.map(task => ({
          task_id: task.id,
          task_name: task.name,
          status: task.status
        })),
        completedTasks: response.data[key].completed_task?.length || 0,
        totalTasks: response.data[key].total_tasks?.length || 0
      }))
    }

    onMounted(() => {
      fetchSprints()
    })
    

    return {
      isTeamRoute,
      navigateToTeam,
      isProjectRoute,
      navigateToProject,
      navigateToSprint,
      sprints
    }
  }
}
</script>

<style scoped>
.sidebar {
  background: #f8f9fa;
  border-right: 1px solid rgba(var(--v-border-color), 0.12);
}

:root[data-theme="dark"] .sidebar {
  background: #1e1e1e;
}

</style>