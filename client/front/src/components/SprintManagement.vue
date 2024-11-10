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
          :class="{ 'active-sprint': new Date(sprint.due_date) >= new Date() }"
        >
          <template v-slot:prepend>
            <v-icon :color="sprint.isActive ? 'primary' : 'grey'">
              mdi-calendar
            </v-icon>
          </template>
  
          <v-list-item-title class="d-flex flex-column">
            <div class="d-flex align-center justify-space-between w-100 mb-2">
              <div>
                <div class="text-subtitle-1">Sprint {{ sprint.name }}</div>
                <div class="text-caption text-grey">
                  {{ formatDate(sprint.start_at) }} - {{ formatDate(sprint.due_date) }}
                </div>
              </div>
              <div class="text-caption">
                {{ sprint.completedTasks }}/{{ sprint.totalTasks }} tasks
              </div>
            </div>
            
            <!-- Sprint的任务接收区 -->
            <Draggable
              :list="sprint.tasks"
              group="tasks"
              :data-sprint-id="sprint.id"
              class="sprint-tasks-container"
              @add="onTaskAdded($event, sprint.id)"
            >
              <template #item="{ element: task }">
                <v-card class="task-card ma-2" flat>
                  <v-card-text class="py-2">
                    <div class="d-flex align-center">
                      <span class="text-body-2">#{{ task.task_id }} {{ task.task_name }}</span>
                      <v-chip size="x-small" class="ml-2" :color="getStatusColor(task.status)">
                        {{ task.status }}
                      </v-chip>
                    </div>
                  </v-card-text>
                </v-card>
              </template>
            </Draggable>
          </v-list-item-title>
        </v-list-item>
      </v-list>
  
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
                    v-model="newSprint.start_at"
                    label="Start Date"
                    type="date"
                    required
                    :rules="[v => !!v || 'Start date is required']"
                  ></v-text-field>
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model="newSprint.due_date"
                    label="End Date"
                    type="date"
                    required
                    :rules="[v => !!v || 'End date is required']"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey" text @click="showNewSprintDialog = false">Cancel</v-btn>
            <v-btn color="primary" @click="createSprints" :disabled="!valid">Create</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </template>
  
  <script>
  import { ref, computed } from 'vue'
  import { format } from 'date-fns'
  import { getSprints, createSprint } from '@/api/sprint'
  import { useToast } from 'vue-toastification'
  import { onMounted } from 'vue'
  import Draggable from 'vuedraggable'
  import { updateTask } from '@/api/task'
  export default {
    name: 'SprintManagement',
    components: {
      Draggable
    },
    props: {
    projectId: {
      type: [Number, String],
      required: true,
      validator(value) {
        return value !== undefined && value !== null
      }
    }
  },
    setup(props) {
      const showNewSprintDialog = ref(false)
      const valid = ref(false)
      const sprints = ref([])
      const form = ref(null)
      const toast = useToast()
  
      const newSprint = ref({
        name: '',
        start_at: '',
        due_date: '',
        project_id: props.projectId
      })
  
      const activeSprint = computed(() => {
        const now = new Date()
        return sprints.value.find(sprint => {
          const dueDate = new Date(sprint.due_date) 
          return dueDate >= now
        })
      })
  
      const formatDate = (date) => {
        return format(new Date(date), 'yyyy-MM-dd')
      }
  
      const createSprints = async () => {
        if (!valid.value) return
        
        try {
          await createSprint(newSprint.value)
          showNewSprintDialog.value = false
          newSprint.value = {
            name: '',
            start_at: '',
            due_date: '',
            project_id: props.projectId
          }
          form.value.reset()
          await fetchSprints()
          toast.success('创建sprint成功')
        } catch (error) {
          toast.error('创建sprint失败')
          console.error('Failed to create sprint:', error)
        }
      }
  
      const fetchSprints = async () => {
        try {
          const response = await getSprints({project_id: props.projectId})
          sprints.value = Object.keys(response.data).map(key => ({
            id: key,
            ...response.data[key],
            completedTasks: response.data[key].tasks?.filter(task => task.completed)?.length || 0,
            totalTasks: response.data[key].tasks?.length || 0
          }))
          
          console.log('转换后的sprints数据:', sprints.value)
        } catch (error) {
          sprints.value = []
          toast.error('获取sprints失败')
          console.error('Failed to fetch sprints:', error)
        }
      }
  
      const onTaskAdded = async (evt, sprintId) => {
        const taskId = evt.item.dataset.taskId
        try {
          // 向后端发送更新请求
          await updateTask({
            task_id: taskId,
            sprint_id: sprintId
          })
          toast.success('任务已添加到Sprint')
          await fetchSprints() // 刷新Sprint列表
        } catch (error) {
          console.error('Failed to update task sprint:', error)
          toast.error('无法更新任务Sprint')
        }
      }
  
      const getStatusColor = (status) => {
        const colors = {
          'Not start': 'grey',
          'Started': 'blue',
          'Testing': 'orange',
          'Review': 'purple',
          'Done': 'success'
        }
        return colors[status] || 'grey'
      }
  
      onMounted(()=>{
        fetchSprints()
      })
  
      return {
        showNewSprintDialog,
        valid,
        sprints,
        form,
        newSprint,
        activeSprint,
        formatDate,
        createSprints,
        fetchSprints,
        onTaskAdded,
        getStatusColor
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
  
  .sprint-tasks-container {
    min-height: 50px;
    padding: 8px;
    margin-top: 8px;
    background-color: rgba(0, 0, 0, 0.03);
    border-radius: 4px;
    transition: background-color 0.2s;
  }
  
  .sprint-tasks-container:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  .task-card {
    background-color: white;
    transition: transform 0.2s;
  }
  
  .task-card:hover {
    transform: translateY(-2px);
  }
  </style>