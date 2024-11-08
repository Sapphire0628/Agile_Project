<template>
    <v-layout>
      <Header />
      <SideBar />
      <v-main>
        <v-container fluid>
          <h1 class="text-h4 mb-6">Project Dashboard</h1>
        </v-container>
      </v-main>
    </v-layout>
  </template>
  
  <script>
  import Header from '@/components/Header.vue'
  import SideBar from '@/components/SideBar.vue'
  
  export default {
    name: 'ProjectView',
    components: {
      Header,
      SideBar
    }
  }
  </script>