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
                <Burndown 
                  ref="burndownRef"
                  :project-id="projectId" 
                  class="h-100"
                />
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
import { defineComponent, ref, computed, watch } from 'vue'
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
    const burndownRef = ref(null)
    const RemoveFromSprint = async () => {
      if (backlog.value && typeof backlog.value.fetchTasks === 'function') {
        await backlog.value.fetchTasks()
      } else {
        console.error('Backlog reference or fetchTasks method not available')
      }
    }
    const SprintCreated = async () => {
      if (sideBar.value?.fetchSprints) {
        await sideBar.value.fetchSprints()
      }
      if (burndownRef.value?.fetchBurndownData) {
        await burndownRef.value.fetchBurndownData()
      }
      else {
        console.error('SideBar reference or fetchSprints method not available')
      }
    }
    const SprintUpdated = async () => {
      if (sprintManagementRef.value?.fetchSprints) {
        await sprintManagementRef.value.fetchSprints()
      }
      if (burndownRef.value?.fetchBurndownData) {
        await burndownRef.value.fetchBurndownData()
      }
      else {
        console.error('SprintManagement reference or fetchSprints method not available')
      }
    }

    const projectId = computed(() => parseInt(route.params.id))

    watch(() => route.params.id, async (newId) => {
      if (burndownRef.value?.fetchBurndownData) {
        await burndownRef.value.fetchBurndownData()
      }
      if (backlog.value?.fetchTasks) {
        await backlog.value.fetchTasks()
      }
      if (sideBar.value?.fetchSprints) {
        await sideBar.value.fetchSprints()
      }
      if (sprintManagementRef.value?.fetchSprints) {
        await sprintManagementRef.value.fetchSprints()
      }
    })

    return {
      projectId,
      RemoveFromSprint,
      SprintCreated,
      SprintUpdated,
      backlog,
      sideBar,
      sprintManagementRef,
      burndownRef
    }
  }
})
</script>