<template>
  <v-layout>
    <Header />
    <SideBar ref="sideBar"/>
    <v-main>
      <v-container fluid>
        <v-row>

          <v-col cols="12" md="8">
            <v-row style="height: 80vh;">
              <v-col cols="12" style="height: 60%;">
                <Burndown :project-id="projectId" class="h-100" />
              </v-col>
              <v-col cols="12" style="height: 40%;">
                <Backlog 
                  ref="backlog"
                  :project-id="projectId" 
                  @sprint-updated="SprintUpdated"
                  class="h-100"
                />
              </v-col>
            </v-row>
          </v-col>

          <v-col cols="12" md="4">
            <SprintManagement :project-id="projectId" @task-removed-from-sprint="RemoveFromSprint" 
            @sprint-created="SprintCreated"
            ref="sprintManagementRef"
            />
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-layout>
</template>

<script>
import { defineComponent, ref } from 'vue'
import { useRoute } from 'vue-router'
import Header from '@/components/Header.vue'
import SideBar from '@/components/SideBar.vue'
import Backlog from '@/components/Backlog.vue'
import SprintManagement from '@/components/SprintManagement.vue'
import Burndown from '@/components/Burndown.vue'

export default defineComponent({
  name: 'ProjectView',
  components: {
    Header,
    SideBar,
    Backlog,
    SprintManagement,
    Burndown
  },
  setup(){
    const route = useRoute()
    const backlog = ref(null)
    const sideBar = ref(null)
    const sprintManagementRef = ref(null)
    const RemoveFromSprint = async () => {
      if (backlog.value && typeof backlog.value.fetchTasks === 'function') {
        await backlog.value.fetchTasks()
      } else {
        console.error('Backlog reference or fetchTasks method not available')
      }
    }
    const SprintCreated = async () => {
      if (sideBar.value && typeof sideBar.value.fetchSprints === 'function') {
        await sideBar.value.fetchSprints()
      }
      else {
        console.error('SideBar reference or fetchSprints method not available')
      }
    }
    const SprintUpdated = async () => {
      if (sprintManagementRef.value && typeof sprintManagementRef.value.fetchSprints === 'function') {
        await sprintManagementRef.value.fetchSprints()
      } else {
        console.error('SprintManagement reference or fetchSprints method not available')
      }
    }

    const projectId = ref(parseInt(route.params.id))
    return {
      projectId,
      RemoveFromSprint,
      SprintCreated,
      SprintUpdated,
      backlog,
      sideBar,
      sprintManagementRef
    }
  }
})
</script>