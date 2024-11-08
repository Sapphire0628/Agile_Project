<template>
    <div class="backlog">
      <div class="d-flex align-center justify-space-between mb-6">
        <div>
          <h2 class="text-h4">Backlog</h2>
          <div class="text-subtitle-1 text-grey">{{ tasks.length }} user stories</div>
        </div>
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          @click="showNewTaskDialog = true"
        >
          USER STORY
        </v-btn>
      </div>
      
      <div class="filters mb-6">
        <div class="d-flex align-center">
          <v-text-field
            v-model="search"
            prepend-inner-icon="mdi-magnify"
            label="Search tasks"
            hide-details
            density="compact"
            class="mr-4"
            style="max-width: 300px"
          ></v-text-field>
          <v-switch
            v-model="showTags"
            label="Tags"
            hide-details
            density="compact"
          ></v-switch>
        </div>
      </div>
  
      <v-table>
        <thead>
          <tr>
            <th class="text-left">ID</th>
            <th class="text-left">Task</th>
            <th class="text-left">Status</th>
            <th class="text-left">Story Points</th>
            <th class="text-left">Assignee</th>
            <th class="text-left">Sprint</th>
            <th class="text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in filteredTasks" :key="task.id" @click="goToTaskDetail(task.id)" style="cursor: pointer">
            <td>#{{ task.id }}</td>
            <td>{{ task.title }}</td>
            <td>
              <v-select
                v-model="task.status"
                :items="statusOptions"
                density="compact"
                variant="outlined"
                hide-details
                class="status-select"
                @click.stop
                @update:model-value="updateTaskStatus(task.id, $event)"
              ></v-select>
            </td>
            <td>
              <v-select
                v-model="task.storyPoints"
                :items="storyPointOptions"
                density="compact"
                variant="outlined"
                hide-details
                class="points-select"
                @click.stop
                @update:model-value="updateTaskPoints(task.id, $event)"
              ></v-select>
            </td>
            <td>
              <v-select
                v-model="task.assigneeId"
                :items="teamMembers"
                item-title="username"
                item-value="id"
                density="compact"
                variant="outlined"
                hide-details
                class="assignee-select"
                @click.stop
                @update:model-value="updateTaskAssignee(task.id, $event)"
              ></v-select>
            </td>
            <td>
              <v-select
                v-model="task.sprintId"
                :items="sprints"
                item-title="name"
                item-value="id"
                density="compact"
                variant="outlined"
                hide-details
                class="sprint-select"
                @click.stop
                @update:model-value="updateTaskSprint(task.id, $event)"
              ></v-select>
            </td>
            <td>
              <v-icon
                icon="mdi-pencil"
                size="small"
                class="mr-2"
                @click.stop="goToTaskDetail(task.id)"
              ></v-icon>
            </td>
          </tr>
        </tbody>
      </v-table>
      <v-dialog v-model="showNewTaskDialog" max-width="500px">
      </v-dialog>
    </div>
  </template>
  
  <script>
  import { ref, computed } from 'vue'
  import { useRouter } from 'vue-router'
  
  export default {
    name: 'Backlog',
    
    setup() {
      const router = useRouter()
      const search = ref('')
      const showTags = ref(false)
      const showNewTaskDialog = ref(false)
      const tasks = ref([])
      const teamMembers = ref([])
      const sprints = ref([])
  
      const statusOptions = [
        'To Do',
        'In Progress',
        'Review',
        'Testing',
        'Done'
      ]
  
      const storyPointOptions = [1, 2, 3, 5, 8, 13, 21]
  
      const filteredTasks = computed(() => {
        return tasks.value.filter(task =>
          task.title.toLowerCase().includes(search.value.toLowerCase())
        )
      })
  
  
      return {
        search,
        showTags,
        showNewTaskDialog,
        tasks,
        teamMembers,
        sprints,
        statusOptions,
        storyPointOptions,
        filteredTasks,
      }
    }
  }
  </script>
  
  <style scoped>
  .backlog {
    padding: 16px;
  }
  
  .status-select,
  .points-select,
  .assignee-select,
  .sprint-select {
    max-width: 150px;
  }
  </style>