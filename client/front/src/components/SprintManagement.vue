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
          <v-card width="100%" class="sprint-card">
            <v-card-item>
              <template v-slot:prepend>
                <v-icon color="primary" size="large">mdi-calendar-clock</v-icon>
              </template>
              
              <div class="d-flex flex-column w-100">
                <div class="d-flex align-center justify-space-between mb-2">
                  <div>
                    <div class="text-h6">Sprint {{ sprint.name }}</div>
                    <div class="text-caption text-grey">
                      {{ formatDate(sprint.start_at) }} - {{ formatDate(sprint.due_date) }}
                    </div>
                  </div>
                  <v-chip
                    :color="getSprintStatusColor(sprint)"
                    size="small"
                  >
                    {{ getSprintStatus(sprint) }}
                  </v-chip>
                </div>

                <div class="progress-container d-flex align-center mb-2">
                  <v-progress-linear
                    :model-value="(sprint.completedTasks / (sprint.totalTasks || 1)) * 100"
                    height="20"
                    rounded
                    color="primary"
                    bg-color="primary-lighten-3"
                    class="flex-grow-1"
                  >
                    <template v-slot:default="{ value }">
                      <div class="progress-text">
                        <strong>{{ Math.ceil(value) }}%</strong>
                      </div>
                    </template>
                  </v-progress-linear>
                </div>

                <div class="d-flex align-center justify-space-between text-caption mb-3">
                  <div class="d-flex align-center">
                    <v-icon size="small" class="mr-1">mdi-checkbox-marked-circle</v-icon>
                    {{ sprint.completedTasks }}/{{ sprint.totalTasks }} Tasks completed
                  </div>
                  <div class="d-flex align-center">
                    <v-icon size="small" class="mr-1">mdi-clock-outline</v-icon>
                    {{ calculateRemainingDays(sprint.due_date) }} Days remaining
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
                    <v-card class="task-card ma-2" 
                      flat 
                      :data-task-id="task.task_id" 
                      :data-sprint-id="sprint.id"
                      :class="{ 'task-done': task.status === 'Done' }"
                    >
                      <v-card-text class="py-2">
                        <div class="d-flex align-center justify-space-between">
                          <div class="d-flex align-center">
                            <span class="text-body-2" :class="{ 'task-title-done': task.status === 'Done' }">
                              #{{ task.task_id }} {{ task.task_name }}
                            </span>
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
              </div>
            </v-card-item>
          </v-card>
        </v-list-item>
      </v-list>
  
      <v-dialog v-model="showNewSprintDialog" max-width="500px">
        <v-card>
          <v-card-title>Sprint {{ newSprint.round }}</v-card-title>
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
                    :min="latestSprintEndDate ? formatDate(new Date(latestSprintEndDate)) : formatDate(new Date())"
                    :rules="getStartDateRules"
                  ></v-text-field>
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model="newSprint.due_date"
                    label="End Date"
                    type="date"
                    required
                    :min="newSprint.start_at"
                    :rules="[
                      v => !!v || 'End date cannot be empty',
                      v => !newSprint.start_at || new Date(v) >= new Date(newSprint.start_at) || 'End date cannot be earlier than start date'
                    ]"
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
    expose: ['fetchSprints'],
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
          toast.success('Task added')
        } catch (error) {
          toast.error('Failed to update task sprint')
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
          toast.success('Sprint created successfully')
          emit('sprint-created')
        } catch (error) {
          toast.error('Failed to create sprint')
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
          toast.error('Failed to fetch sprints')
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
          toast.success('Task moved back to backlog')
        } catch (error) {
          console.error('Failed to remove task from sprint:', error)
          toast.error('Failed to move task back to backlog')
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
        if (latestSprintEndDate.value) {
          const nextDay = new Date(latestSprintEndDate.value)
          nextDay.setDate(nextDay.getDate() + 1)
          newSprint.value.start_at = formatDate(nextDay)
        }
        showNewSprintDialog.value = true
      }
  
      const calculateRemainingDays = (dueDate) => {
        const now = new Date()
        const due = new Date(dueDate)
        const diffTime = due - now
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
        return diffDays > 0 ? diffDays : 0
      }
  
      const getSprintStatus = (sprint) => {
        const now = new Date()
        const startDate = new Date(sprint.start_at)
        const dueDate = new Date(sprint.due_date)
        
        if (now < startDate) return 'Not started'
        if (now > dueDate) return 'Ended'
        return 'In progress'
      }
  
      const getSprintStatusColor = (sprint) => {
        const now = new Date()
        const startDate = new Date(sprint.start_at)
        const dueDate = new Date(sprint.due_date)
        
        if (now < startDate) return 'grey'
        if (now > dueDate) return 'error'
        return 'primary'
      }

      const latestSprintEndDate = computed(() => {
        if (!sprints.value.length) return null;
        return sprints.value.reduce((latest, sprint) => {
          const dueDate = new Date(sprint.due_date);
          return dueDate > latest ? dueDate : latest;
        }, new Date(sprints.value[0].due_date));
      });

      const getStartDateRules = computed(() => {
        const baseRules = [
          v => !!v || 'Start date cannot be empty',
          v => new Date(v) >= new Date(formatDate(new Date())) || 'Start date cannot be earlier than today'
        ];
        
        if (latestSprintEndDate.value) {
          baseRules.push(
            v => new Date(v) > latestSprintEndDate.value || 'New sprint start time must be later than the end time of the existing sprint'
          );
        }
        
        return baseRules;
      });

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
        openNewSprintDialog,
        calculateRemainingDays,
        getSprintStatus,
        getSprintStatusColor,
        getStartDateRules,
        latestSprintEndDate
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
  
  .progress-container {
    position: relative;
    width: 100%;
  }
  
  .progress-text {
    color: white;
    text-shadow: 1px 1px 1px rgba(0,0,0,0.2);
    font-size: 0.875rem;
  }
  
  .v-progress-linear {
    border-radius: 10px;
    overflow: hidden;
  }
  
  .task-done {
    background-color: #f5f5f5;
    opacity: 0.8;
    border: none;
  }
  
  .task-title-done {
    color: #9e9e9e;
    text-decoration: line-through;
  }
  
  .task-done:hover {
    transform: none !important;
  }
  
  .task-done .task-meta .v-chip {
    opacity: 0.7;
  }
  </style>