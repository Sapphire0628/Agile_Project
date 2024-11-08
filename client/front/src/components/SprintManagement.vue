<template>
    <div class="sprint-management">
      <div class="d-flex align-center justify-space-between mb-4">
        <div>
          <h2 class="text-h5">Sprints</h2>
          <div class="text-subtitle-2 text-grey">
            {{ activeSprint ? `Current: Sprint ${activeSprint.name}` : 'No active sprint' }}
          </div>
        </div>
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          @click="showNewSprintDialog = true"
        >
          New Sprint
        </v-btn>
      </div>
  
      <v-list class="sprint-list">
        <v-list-item
          v-for="sprint in sprints"
          :key="sprint.id"
          :class="{ 'active-sprint': sprint.isActive }"
        >
          <template v-slot:prepend>
            <v-icon :color="sprint.isActive ? 'primary' : 'grey'">
              mdi-calendar
            </v-icon>
          </template>
  
          <v-list-item-title class="d-flex align-center justify-space-between">
            <div>
              <div class="text-subtitle-1">Sprint {{ sprint.name }}</div>
              <div class="text-caption text-grey">
                {{ formatDate(sprint.startDate) }} - {{ formatDate(sprint.endDate) }}
              </div>
            </div>
            <div class="text-caption">
              {{ sprint.completedTasks }}/{{ sprint.totalTasks }} tasks
            </div>
          </v-list-item-title>
        </v-list-item>
      </v-list>
  
      <!-- 新建Sprint对话框 -->
      <v-dialog v-model="showNewSprintDialog" max-width="500px">
        <v-card>
          <v-card-title>New Sprint</v-card-title>
          <v-card-text>
            <v-form ref="form" v-model="valid">
              <v-text-field
                v-model="newSprint.name"
                label="Sprint Name"
                required
                :rules="[v => !!v || 'Name is required']"
              ></v-text-field>
              
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    v-model="newSprint.startDate"
                    label="Start Date"
                    type="date"
                    required
                    :rules="[v => !!v || 'Start date is required']"
                  ></v-text-field>
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model="newSprint.endDate"
                    label="End Date"
                    type="date"
                    required
                    :rules="[v => !!v || 'End date is required']"
                  ></v-text-field>
                </v-col>
              </v-row>
  
              <v-textarea
                v-model="newSprint.goal"
                label="Sprint Goal"
                rows="3"
              ></v-textarea>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey" text @click="showNewSprintDialog = false">Cancel</v-btn>
            <v-btn color="primary" @click="createSprint" :disabled="!valid">Create</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </template>
  
  <script>
  import { ref, computed } from 'vue'
  import { format } from 'date-fns'
  
  export default {
    name: 'SprintManagement',
    
    setup() {
      const showNewSprintDialog = ref(false)
      const valid = ref(false)
      const sprints = ref([])
      const form = ref(null)
  
      const newSprint = ref({
        name: '',
        startDate: '',
        endDate: '',
        goal: ''
      })
  
      const activeSprint = computed(() => 
        sprints.value.find(sprint => sprint.isActive)
      )
  
      const formatDate = (date) => {
        return format(new Date(date), 'dd MMM yyyy')
      }
  
      const createSprint = async () => {
        if (!valid.value) return
        
        try {
          // 调用API创建Sprint
          await createSprintAPI(newSprint.value)
          showNewSprintDialog.value = false
          // 重置表单
          newSprint.value = {
            name: '',
            startDate: '',
            endDate: '',
            goal: ''
          }
          form.value?.reset()
          // 刷新Sprint列表
          await fetchSprints()
        } catch (error) {
          console.error('Failed to create sprint:', error)
        }
      }
  
      const fetchSprints = async () => {
        try {
          const response = await getSprintsAPI()
          sprints.value = response.data
        } catch (error) {
          console.error('Failed to fetch sprints:', error)
        }
      }
  
      return {
        showNewSprintDialog,
        valid,
        sprints,
        form,
        newSprint,
        activeSprint,
        formatDate,
        createSprint
      }
    }
  }
  </script>
  
  <style scoped>
  .sprint-management {
    padding: 16px;
    background-color: #f5f5f5;
    border-radius: 8px;
  }
  
  .sprint-list {
    max-height: 400px;
    overflow-y: auto;
  }
  
  .active-sprint {
    background-color: rgba(var(--v-theme-primary), 0.05);
  }
  
  .v-list-item {
    margin-bottom: 8px;
    border-radius: 4px;
  }
  </style>