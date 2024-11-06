<template>
  <v-card class="mx-auto pa-6 mt-15" max-width="800">
    <div class="text-center mb-6">
      <h1 class="text-h4">Scrum</h1>
    </div>
    <v-form @submit.prevent="createProject">
      <v-text-field
        variant="outlined"
        v-model="project_name"
        label="项目名称"
        required
        :rules="[v => !!v || '项目名称是必填的']"
        class="mb-4"
      ></v-text-field>

      <v-textarea
        variant="outlined"
        v-model="description"
        label="项目描述"
        required
        :rules="[v => !!v || '项目描述是必填的']"
        rows="6"
      ></v-textarea>
      <div class="d-flex justify-center mt-2">
        <v-btn
          rounded="lg"
          color="grey-lighten-1"
          @click="$router.back()"
          min-width="120"
          class="mr-8"
        >
          返回
        </v-btn>
        <v-btn
          rounded="lg"
          color="indigo"
          type="submit"
          min-width="120"
        >
          创建项目
        </v-btn>
      </div>
    </v-form>
  </v-card>
</template>

<script>
import { addProject } from '@/api/project'

export default {
  name: 'NewProject',
  data() {
    return {
      project_name: '',
      description: '',
    }
  },
  methods: {
    async createProject() {
      try {
        const response = await addProject({project_name: this.project_name, description: this.description})
        this.$router.back()
        console.log(response)
      } catch (err) {
        console.error('获取项目失败:', err)
      }
    }
  }
}
</script>