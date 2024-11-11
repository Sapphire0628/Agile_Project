<template>
   <v-layout>
    <Header />
    <SideBar />
    <v-main>
      <Dashboard 
      :sprint-id="sprintId"
      :sprint-name="sprintName"
      :project-id="projectId" />
    </v-main>
  </v-layout>
</template>
  
<script>
import Header from '@/components/Header.vue'
import SideBar from '@/components/SideBar.vue'
import Dashboard from '@/components/Dashboard.vue'
import { useRoute } from 'vue-router'
export default {
  name: 'SprintDashboard',
  components: {
    Header,
    SideBar,
    Dashboard
  },
  setup() {
    const route = useRoute()
    const sprintId = route.params.sprintId
    const sprintName = route.params.sprintName
    const projectId = route.params.id
    return {
      sprintId,
      sprintName,
      projectId
    }
  }
}
</script>
