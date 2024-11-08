<template>
  <v-layout>
    <Header />
    <SideBar />
    <v-main>
      <v-container fluid>
        <v-row>
          <!-- 左侧Backlog -->
          <v-col cols="12" md="8">
            <Backlog />
          </v-col>
          
          <!-- 右侧Sprint管理 -->
          <v-col cols="12" md="4">
            <SprintManagement />
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-layout>
</template>

<script>
import { defineComponent } from 'vue'
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
  }
})
</script>