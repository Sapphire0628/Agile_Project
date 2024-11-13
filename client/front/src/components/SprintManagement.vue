<template>
    <div class="sprint-management">
      <div class="d-flex align-center justify-space-between mb-4">
        <div>
          <h2 class="text-h5">Sprints</h2>
          <div class="text-subtitle-2 text-grey">
            {{ sprintsData.length > 0 ? `Current: Sprint ${sprintsData[0].name}` : 'No active sprint' }}
          </div>
        </div>
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          @click="openNewSprintDialog"
        >
          New Sprint
        </v-btn>
      </div>
  
      <v-list class="sprint-list">
        <v-list-item
          v-for="sprint in sprintsData"
          :key="sprint.id"
          class="active-sprint"
        >
          <template v-slot:prepend>
            <v-icon color="primary">
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
            
            <Draggable
              :list="sprint.tasks"
              group="tasks"
              item-key="id"
              :data-sprint-id="sprint.id"
              class="sprint-tasks-container"
              @add="onTaskAdded($event, sprint.id)"
              @remove="fetchSprints"
            >
              <template #item="{ element: task }">
                <v-card class="task-card ma-2" flat :data-task-id="task.task_id" :data-sprint-id="sprint.id">
                  <v-card-text class="py-2">
                    <div class="d-flex align-center justify-space-between">
                      <div class="d-flex align-center">
                        <span class="text-body-2">#{{ task.task_id }} {{ task.task_name }}</span>
                        <v-chip size="x-small" class="ml-2" :color="getStatusColor(task.status)">
                          {{ task.status }}
                        </v-chip>
                      </div>
                      <v-btn
                        icon="mdi-close"
                        size="x-small"
                        variant="text"
                        @click="removeTaskFromSprint(task.task_id, sprint.id)"
                      ></v-btn>
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
          <v-card-title>新建 Sprint {{ newSprint.round }}</v-card-title>
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
  import { ref, computed, watch } from 'vue'
  import { format } from 'date-fns'
  import { getSprints, createSprint } from '@/api/sprint'
  import { useToast } from 'vue-toastification'
  import { onMounted } from 'vue'
  import Draggable from 'vuedraggable'
  import { updateSprintTask } from '@/api/sprint'
  export default {
    name: 'SprintManagement',
    components: {
      Draggable
    },
    emits: ['task-removed-from-sprint','sprint-created'],
    props: {
    projectId: {
      type: [Number, String],
      required: true,
      validator(value) {
        return value !== undefined && value !== null
      }
    }
  },
    setup(props, { emit }) {
      const showNewSprintDialog = ref(false)
      const valid = ref(false)
      const sprints = ref([])
      const form = ref(null)
      const toast = useToast()
  
      const newSprint = ref({
        name: '',
        start_at: '',
        due_date: '',
        project_id: props.projectId,
        round: 0
      })
  
      const onTaskAdded = async (evt, newsprintId) => {
        const taskId = evt.item.dataset.taskId
        const oldSprintId = evt.item.dataset.sprintId
        const fromBacklog = evt.from.classList.contains('task-container')

        if (!taskId || !newsprintId) {
          console.error('Missing task ID or sprint ID')
          return
        }
        if(!fromBacklog&&oldSprintId&&oldSprintId!==newsprintId){
          try {
            await updateSprintTask({
              round: oldSprintId,
              type: 'remove',
              tasks: [taskId],
              project_id: props.projectId
            })
          await updateSprintTask({
            round: newsprintId,
            type: 'add',
            tasks: [taskId],
            project_id: props.projectId
          })
          await fetchSprints()
          toast.success('任务已添加')
        } catch (error) {
          toast.error('无法更新任务Sprint')
          await fetchSprints()
          }
        }
      }
      
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
          newSprint.value.round = getNextRound()
          
          await createSprint(newSprint.value)
          showNewSprintDialog.value = false
          newSprint.value = {
            name: '',
            start_at: '',
            due_date: '',
            project_id: props.projectId,
            round: 0
          }
          form.value?.reset()
          await fetchSprints()
          toast.success('创建sprint成功')
          emit('sprint-created')
        } catch (error) {
          toast.error('创建sprint失败')
          console.error('Failed to create sprint:', error)
        }
      }
  
      const isLoadingSprints = ref(false)
  
      const fetchSprints = async () => {
        isLoadingSprints.value = true
        try {
          const response = await getSprints({ project_id: props.projectId })
          sprints.value = Object.keys(response.data).map(key => ({
            id: key,
            ...response.data[key],
            tasks: response.data[key].total_tasks.map(task => ({
              task_id: task.id,
              task_name: task.name,
              status: task.status
            })),
            completedTasks: response.data[key].completed_task?.length || 0,
            totalTasks: response.data[key].total_tasks?.length || 0
          }))
          sprints.value = sprints.value
            .sort((a, b) => new Date(a.start_at) - new Date(b.start_at))
            .map((sprint, index) => ({
              ...sprint,
              round: sprint.round || index 
            }))
        } catch (error) {
          console.error('Failed to fetch sprints:', error)
          toast.error('获取sprints失败')
          sprints.value = []
        } finally {
          isLoadingSprints.value = false
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

      const sprintsData = ref([])

      watch(() => sprints.value, (newSprints) => {
        const now = new Date()
        sprintsData.value = newSprints.filter(sprint => {
          const dueDate = new Date(sprint.due_date)
          return dueDate >= now
        }).sort((a, b) => new Date(a.start_at) - new Date(b.start_at))
      }, { immediate: true })
  
      watch(() => props.projectId, () => {
        fetchSprints()
      })
  
      const removeTaskFromSprint = async (taskId, sprintId) => {
        try {
          await updateSprintTask({
            round: sprintId,
            type: 'remove',
            tasks: [taskId],
            project_id: props.projectId
          })
          await fetchSprints()
          emit('task-removed-from-sprint')
          toast.success('任务已移回Backlog')
        } catch (error) {
          console.error('Failed to remove task from sprint:', error)
          toast.error('无法移除任务')
          await fetchSprints()
        }
      }
  
      onMounted(()=>{
        fetchSprints()
      })
  
      const getNextRound = () => {
        if (!sprints.value.length) return 0
        const maxRound = Math.max(...sprints.value.map(sprint => sprint.round || 0))
        return maxRound + 1
      }
  
      const openNewSprintDialog = () => {
        newSprint.value.round = getNextRound()
        showNewSprintDialog.value = true
      }
  
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
        getStatusColor,
        sprintsData,
        isLoadingSprints,
        removeTaskFromSprint,
        openNewSprintDialog
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
  
  .sprint-tasks-container.dragover {
    background-color: rgba(var(--v-theme-primary), 0.1);
  }
  
  .task-card {
    background-color: white;
    transition: transform 0.2s;
    cursor: move;
  }
  
  .task-card:hover {
    transform: translateY(-2px);
  }
  </style>