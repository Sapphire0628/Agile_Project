<template>
  <div class="dashboard">
    <!-- 头部信息 -->
    <header class="mb-6">
      <div class="d-flex justify-space-between align-center">
        <div>
          <h2 class="text-h4">{{ sprintName }}</h2>
          <div class="text-subtitle-1 text-grey">
            {{ sprintStart }} to {{ sprintEnd }}
          </div>
        </div>
        <div class="sprint-metrics d-flex align-center">
          <v-chip class="mr-2" color="primary">{{ completionRate }}%</v-chip>
          <v-chip class="mr-2">{{ totalPoints }} points</v-chip>
          <v-chip class="mr-2">{{ openTasks }} open</v-chip>
          <v-chip>{{ closedTasks }} closed</v-chip>
        </div>
      </div>
    </header>

    <div class="task-board d-flex">
      <div
        v-for="status in taskStatuses"
        :key="status"
        class="status-column"
        :data-status="status"
      >
        <v-card class="h-100" >
          <v-card-title class="column-header" :style="{ backgroundColor: `${getTitleColor(status)}!important` }">
            {{ status }}
            <v-chip class="ml-2" size="small">
              {{ tasksByStatus[status]?.length || 0 }}
            </v-chip>
          </v-card-title>
          
          <v-card-text class="column-content">
            <Draggable
              v-model="tasksByStatus[status]"
              :group="{ name: 'tasks', pull: true, put: true}"
              item-key="task_id"
              @end="onDragEnd"
              :animation="200"
              ghost-class="ghost-card"
              drag-class="drag-card"
              class = "draggable-container"
            >
              <template #item="{ element: task }">
                <v-card
                  :key="task.task_id"
                  class="task-card mb-3"
                  elevation="1"
                  :data-task-id="task.task_id"
                  @click="openTaskCard(task)"
                >
                  <v-card-text>
                    <div class="d-flex justify-space-between align-center">
                      <div class="task-info">
                        <div class="task-title">
                          <span class="task-id">#{{ task.task_id }}</span>
                          {{ task.task_name }}
                        </div>
                      </div>
                      
                      <div class="task-meta d-flex align-center">
                        <v-chip
                          size="small"
                          :color="getStatusColor(task.status)"
                          class="ml-2"
                        >
                          {{ task.priority || 0 }} points
                        </v-chip>
                      </div>
                    </div>
                  </v-card-text>
                </v-card>
              </template>
            </Draggable>
          </v-card-text>
        </v-card>
      </div>
    </div>
  </div>
  <TaskCard 
    v-model="showTaskCard"
    :task-id="selectedTaskId"
    :task-statuses="taskStatuses"
    :project-id="projectId"
    @task-updated="fetchTasks"
  />
</template>

<script>
import { ref, onMounted, computed, watch} from 'vue'
import Draggable from 'vuedraggable'
import { useToast } from 'vue-toastification'
import { updateTask } from '@/api/task'
import { getSprints } from '@/api/sprint'
import { useRoute } from 'vue-router'
import TaskCard from './TaskCard.vue'

export default {
  name: 'Dashboard',
  components: {
    Draggable,
    TaskCard
  },
  props: {
    sprintId: {
      type: [Number, String],
      required: true
    },
    sprintName: {
      type: String,
      required: true
    },
    projectId: {
      type: [Number, String],
      required: true
    }
  },
  setup(props) {
    const route = useRoute()
    const toast = useToast()
    const taskStatuses = ['Not start', 'Started', 'Testing', 'Review', 'Done']
    const tasksByStatus = ref({})
    const sprintStart = ref('')
    const sprintEnd = ref('')
    const showTaskCard = ref(false)
    const selectedTaskId = ref('')

    const openTaskCard = (task) => {
      if (task && task.task_id) {
      selectedTaskId.value = task.task_id
        showTaskCard.value = true
      }
    }

    const getTitleColor = (status) => {
      const colors = {
        'Not start': 'rgba(158, 158, 158, 0.2)',  
        'Started': 'rgba(33, 150, 243, 0.2)',     
        'Testing': 'rgba(255, 152, 0, 0.2)',      
        'Review': 'rgba(156, 39, 176, 0.2)',     
        'Done': 'rgba(76, 175, 80, 0.2)'          
      }
      return colors[status] || 'rgba(158, 158, 158, 0.2)'
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


    const completionRate = computed(() => {
      const complte = tasksByStatus.value['Done']?.length || 0
      const total = Object.values(tasksByStatus.value).reduce((acc, curr) => acc + curr.length, 0)
      return Math.round((complte / total) * 100)
    })

    const totalPoints = computed(() => {
      return Object.values(tasksByStatus.value).flat().reduce((acc, task) => acc + (task.priority || 0), 0)
    })

    const openTasks = computed(() => {
      const completed = tasksByStatus.value['Done']?.length || 0
      const total = Object.values(tasksByStatus.value).reduce((acc, curr) => acc + curr.length, 0)
      return total - completed
    })

    const closedTasks = computed(() => {
      return tasksByStatus.value['Done']?.length || 0
    })

    const fetchTasks = async () => {
      try {
        const response = await getSprints({ project_id: props.projectId, round: props.sprintId })
        tasksByStatus.value = {
          'Not start': [],
          'Started': [],
          'Testing': [],
          'Review': [],
          'Done': []
        }
        response.data.total_tasks.forEach(task => {
          if (tasksByStatus.value[task.status]) {
            tasksByStatus.value[task.status].push({
                task_id: task.id,
                task_name: task.name,
                status: task.status,
                assignee: task.members[0] || null,
                priority: task.priority || 0
            })
          }
        })
        sprintStart.value = response.data.start_at
        sprintEnd.value = response.data.due_date
      } catch (error) {
        toast.error('无法获取任务')
      }
    }

    const onDragEnd = async (evt) => {
      if (evt.from === evt.to) return
      try {
        const taskId = evt.item.dataset.taskId
        const newStatus = evt.to.closest('.status-column').getAttribute('data-status')
        await updateTask({task_id: taskId, status: newStatus})
        await fetchTasks()
        toast.success('任务状态更新成功')
      } catch (error) {
        toast.error('任务状态更新失败')
        await fetchTasks()
      }
    }

    watch(
      () => route.params.sprintId,
      (newSprintId) => {
        if (newSprintId) {
          fetchTasks()
        }
      },
      { immediate: true }
    )

    watch(showTaskCard, (newVal) => {
      if (!newVal) {
        selectedTaskId.value = null
      }
    })

    onMounted(() => {
      fetchTasks()
    })

    return {
      taskStatuses,
      tasksByStatus,
      completionRate,
      totalPoints,
      openTasks,
      closedTasks,
      getStatusColor,
      onDragEnd,
      sprintStart,
      sprintEnd,
      openTaskCard,
      showTaskCard,
      selectedTaskId,
      fetchTasks,
      getTitleColor
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 24px;
  overflow: hidden;
}

.task-board {
  gap: 20px;
  height: calc(100vh - 200px);
  display: flex;
  overflow-x: auto;
  padding-bottom: 16px;
  margin-right: -24px;
  padding-right: 24px;
}

.status-column {
  flex: 0 0 250px;
  min-width: 250px;
  margin-right: 20px;
}

.status-column:last-child {
  margin-right: 0;
}

.column-header {
  font-size: 1rem;
  font-weight: 500;
  padding: 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

.column-content {
  height: calc(100% - 64px);
  overflow-y: auto;
  padding: 0 !important;
}

.task-card {
  cursor: move;
  margin-bottom: 8px !important;
  transition: transform 0.2s, box-shadow 0.2s;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
}

.task-title {
  font-weight: 500;
  font-size: 0.9rem;
}

.task-id {
  color: rgba(0, 0, 0, 0.6);
  margin-right: 8px;
}

.task-meta {
  gap: 8px;
}

.ghost-card {
  opacity: 0.5;
  background-color: #f0f0f0;
  border: 2px dashed #ccc;
}

.drag-card {
  cursor: grabbing;
}

.draggable-container {
  min-height: 100%;
  height: 100%;
  padding: 8px;
}

.sortable-ghost {
  opacity: 0.5;
  background: #c8ebfb !important;
}

.sortable-drag {
  opacity: 0.9;
}

.status-column .column-content:empty::after {
  content: '拖放任务到这里';
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
  font-size: 0.9rem;
  font-style: italic;
}

:deep(.v-card-title) {
  background-color: transparent !important;
}

.status-column .v-card {
  background-color: white; 
}

</style>
