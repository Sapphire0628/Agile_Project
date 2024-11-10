<template>
  <v-layout>
    <Header />
    <SideBar />
    <v-main>
      <v-container fluid>
        <v-row>

          <v-col cols="12" md="8">
            <Backlog :project-id="projectId" />
          </v-col>

          <v-col cols="12" md="4">
            <SprintManagement :project-id="projectId" />
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

export default defineComponent({
  name: 'ProjectView',
  components: {
    Header,
    SideBar,
    Backlog,
    SprintManagement
  },
  setup(){
    const route = useRoute()
    const projectId = ref(parseInt(route.params.id))
    return {
      projectId
    }
  }
})
</script>