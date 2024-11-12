<template>
   <v-layout>
    <Header />
    <SideBar />
    <v-main>
      <Dashboard 
      :sprint-id="$route.params.sprintId"
      :sprint-name="$route.params.sprintName"
      :project-id="$route.params.id" />
    </v-main>
  </v-layout>
</template>
  
<script>
import Header from '@/components/Header.vue'
import SideBar from '@/components/SideBar.vue'
import Dashboard from '@/components/Dashboard.vue'

export default {
  name: 'SprintDashboard',
  components: {
    Header,
    SideBar,
    Dashboard
  }
}
</script>
