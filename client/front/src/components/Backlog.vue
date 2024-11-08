<template>
    <div class="backlog">
      <div class="mb-6 d-flex justify-space-between align-center">
        <div>
          <h2 class="text-h4">Backlog</h2>
          <div class="text-subtitle-1 text-grey">
            {{ tasks.length }} tasks · Total: {{ totalStoryPoints }} points
          </div>
        </div>
      </div>
      
      <div class="filters mb-6">
        <div class="d-flex align-center justify-space-between">
          <v-text-field
            v-model="search"
            prepend-inner-icon="mdi-magnify"
            label="Search tasks"
            hide-details
            density="compact"
            style="max-width: 300px"
          ></v-text-field>
          <v-btn
            color="primary"
            icon
            size="small"
            elevation="1"
            @click="showNewTaskDialog = true"
          >
            <v-icon>mdi-plus</v-icon>
          </v-btn>
        </div>
      </div>
  
      <v-table>
        <thead>
          <tr>
            <th class="text-left" style="width: 100px">ID</th>
            <th class="text-left">Task</th>
            <th class="text-left" style="width: 150px">Status</th>
            <th class="text-left" style="width: 150px">Points</th>
            <th class="text-left" style="width: 50px">Actions</th>
          </tr>
        </thead>
        <tbody>
          <Draggable 
            v-model="tasks" 
            group="tasks"
            item-key="id"
            @end="onDragEnd"
          >
            <template #item="{ element: task }">
              <tr :key="task.id" class="task-row">
                <td>
                  <router-link 
                    :to="{ name: 'TaskDetail', params: { id: task.id }}"
                    class="task-id"
                  >
                    #{{ task.id }}
                  </router-link>
                </td>
                <td>{{ task.title }}</td>
                <td>
                  <v-select
                    v-model="task.status"
                    :items="statusOptions"
                    density="compact"
                    variant="outlined"
                    hide-details
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
                    @click.stop
                    @update:model-value="updateTaskPoints(task.id, $event)"
                  ></v-select>
                </td>
                <td>
                  <v-menu>
                    <template v-slot:activator="{ props }">
                      <v-btn
                        icon="mdi-dots-vertical"
                        size="small"
                        v-bind="props"
                      ></v-btn>
                    </template>
                    <v-list>
                      <v-list-item
                        @click="openEditDialog(task)"
                        prepend-icon="mdi-pencil"
                      >
                        编辑
                      </v-list-item>
                      <v-list-item
                        @click="confirmDelete(task.id)"
                        prepend-icon="mdi-delete"
                        color="error"
                      >
                        删除
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </td>
              </tr>
            </template>
          </Draggable>
        </tbody>
      </v-table>

      <v-dialog v-model="editDialog" max-width="500px">
        <v-card>

        </v-card>
      </v-dialog>


      <v-dialog v-model="deleteDialog" max-width="400px">
        <v-card>

        </v-card>
      </v-dialog>

      <v-dialog v-model="showNewTaskDialog" max-width="800px">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center pa-4">
            <span class="text-h5">New Task</span>
            <v-btn
              icon="mdi-close"
              size="small"
              variant="text"
              @click="closeModal"
            ></v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-row>
              <v-col cols="8">
                <v-form ref="form">
                  <v-text-field
                    v-model="newTask.title"
                    label="Task name"
                    variant="outlined"
                    class="mb-4"
                    :rules="[v => !!v || 'Task name is required']"
                  ></v-text-field>

                  <v-textarea
                    v-model="newTask.description"
                    label="Description"
                    variant="outlined"
                    rows="6"
                  ></v-textarea>
                </v-form>
              </v-col>

              <v-col cols="4">
                <v-select
                  v-model="newTask.status"
                  :items="statusOptions"
                  label="Status"
                  variant="outlined"
                  class="mb-6"
                ></v-select>

                <div class="points-selector">
                  <v-text-field
                    v-model="newTask.storyPoints"
                    label="Story Points"
                    readonly
                    @click="showPointsMenu = !showPointsMenu"
                    variant="outlined"
                    append-inner-icon="mdi-chevron-down"
                  ></v-text-field>
                  
                  <div v-if="showPointsMenu" class="points-dropdown" v-click-outside="closePointsMenu">
                    <div class="points-container">
                      <div
                        v-for="point in storyPointsWithDesc"
                        :key="point.value"
                        class="point-item"
                        :class="{ 'selected': newTask.storyPoints === point.value }"
                        @click="selectPoints(point.value)"
                      >
                        <v-tooltip location="top">
                          <template v-slot:activator="{ props }">
                            <div v-bind="props">{{ point.value }}</div>
                          </template>
                          {{ point.description }}
                        </v-tooltip>
                      </div>
                    </div>
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-actions class="pa-4">
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              @click="createTask"
              :loading="isLoading"
            >
              Create
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </template>
  
  <script>
  import { ref, computed } from 'vue'
  import { useRouter } from 'vue-router'
  import Draggable from 'vuedraggable'
  import { getTasks, addTask } from '@/api/task'
  
  export default {
    name: 'Backlog',
    components: {
      Draggable
    },
    
    directives: {
      clickOutside: {
        mounted(el, binding) {
          el._clickOutside = (event) => {
            if (!(el === event.target || el.contains(event.target))) {
              binding.value(event)
            }
          }
          document.addEventListener('mousedown', el._clickOutside)
        },
        unmounted(el) {
          document.removeEventListener('mousedown', el._clickOutside)
        }
      }
    },
    
    setup() {
      const router = useRouter()
      const search = ref('')
      const showNewTaskDialog = ref(false)
      const showPointsMenu = ref(false)
      const tasks = ref([])
      const teamMembers = ref([])
      const sprints = ref([])
      const editDialog = ref(false)
      const deleteDialog = ref(false)
      const currentTask = ref(null)
      const isLoading = ref(false)
      const form = ref(null)
  
      const statusOptions = [
        'Not start',
        'Started',
        'Testing',
        'Review',
        'Done'
      ]
  
      const storyPointOptions = [ 0,  1, 2, 3, 5, 8, 10, 13, 20, 40]
  
      const filteredTasks = computed(() => {
        return tasks.value.filter(task =>
          task.title.toLowerCase().includes(search.value.toLowerCase())
        )
      })
  
      const onDragEnd = (evt) => {
        const { from, to } = evt
        if (from === to) return 
        
        if (to.dataset.sprintId) {
          const taskId = evt.item.dataset.taskId
          const sprintId = to.dataset.sprintId
          moveTaskToSprint(taskId, sprintId)
        }
      }
  
      const openEditDialog = (task) => {
        currentTask.value = {...task}
        editDialog.value = true
      }
  
      const confirmDelete = (taskId) => {
        currentTask.value = taskId
        deleteDialog.value = true
      }
  
      const newTask = ref({
        title: '',
        description: '',
        status: 'Not start',
        storyPoints: null
      })

      const resetForm = () => {
        newTask.value = {
          title: '',
          description: '',
          status: 'Not start',
          storyPoints: null
        }
        if (form.value) {
          form.value.resetValidation()
        }
      }
  
      const createTask = async () => {
        if (!form.value.validate()) return

        try {
          isLoading.value = true

          // await createTaskAPI(newTask.value)
          await addTask(newTask.value)
          showNewTaskDialog.value = false
          resetForm()

        } catch (error) {
          console.error('Failed to create task:', error)
 
        } finally {
          isLoading.value = false
        }
      }
  
      const selectPoints = (point) => {
        newTask.value.storyPoints = point
        showPointsMenu.value = false
      }
  
      const closePointsMenu = () => {
        showPointsMenu.value = false
      }
  
      const closeModal = () => {
        showNewTaskDialog.value = false
        resetForm()
      }

      const storyPointsWithDesc = [
        { value: 0, description: '无需估算的任务' },
        { value: 1, description: '非常简单，2小时内可完成' },
        { value: 2, description: '简单任务，半天内可完成' },
        { value: 3, description: '中等任务，1天内可完成' },
        { value: 5, description: '较复杂任务，需要2-3天' },
        { value: 8, description: '复杂任务，需要3-5天' },
        { value: 13, description: '较大型任务，需要1-2周' },
        { value: 20, description: '大型任务，建议考虑拆分' },
        { value: 40, description: '特大型任务，必须拆分' }
      ]

      const totalStoryPoints = computed(() => {
        return tasks.value.reduce((sum, task) => sum + (Number(task.storyPoints) || 0), 0)
      })
  

  

      const moveTaskToSprint = (taskId, sprintId) => {
        const task = tasks.value.find(t => t.id === taskId)
        const sprint = sprints.value.find(s => s.id === sprintId)
        
        if (task && sprint) {

          // await updateTaskSprint(taskId, sprintId)
          
          sprint.tasks.push(task)
          tasks.value = tasks.value.filter(t => t.id !== taskId)
        }
      }
  
      return {
        search,
        showNewTaskDialog,
        showPointsMenu,
        tasks,
        teamMembers,
        sprints,
        statusOptions,
        storyPointOptions,
        filteredTasks,
        editDialog,
        deleteDialog,
        currentTask,
        onDragEnd,
        openEditDialog,
        confirmDelete,
        newTask,
        createTask,
        selectPoints,
        closePointsMenu,
        isLoading,
        closeModal,
        storyPointsWithDesc,
        totalStoryPoints,
        moveTaskToSprint
      }
    }
  }
  </script>
  
  <style scoped>
  .backlog {
    padding: 16px;
  }
  
  .sprint-select {
    max-width: 150px;
  }
  
  .task-row {
    cursor: move;
  }
  
  .task-id {
    color: primary;
    text-decoration: none;
  }
  
  .task-id:hover {
    text-decoration: underline;
  }

  .v-card-title {
    border-bottom: 1px solid rgba(0, 0, 0, 0.12);
  }

  .points-selector {
    position: relative;
    width: 100%;
    z-index: 1000;
  }

  .points-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    z-index: 1001;
  }

  .points-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 4px;
    padding: 8px;
  }

  .point-item {
    padding: 8px;
    text-align: center;
    cursor: pointer;
    border-radius: 4px;
  }

  .point-item:hover {
    background-color: #f5f5f5;
    color: #1976d2;
  }

  .point-item.selected {
    color: #1976d2;
    background-color: #e3f2fd;
  }

  @keyframes dropdownFade {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .points-dropdown::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 8px;
    box-shadow: 
      0 4px 6px rgba(0, 0, 0, 0.05),
      0 10px 15px rgba(0, 0, 0, 0.1);
    z-index: -1;
  }


  .point-item {
    position: relative;
    overflow: hidden;
  }

  .point-item::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 100%;
    height: 100%;
    background-color: rgba(25, 118, 210, 0.08);
    border-radius: 50%;
    transform: translate(-50%, -50%) scale(0);
    opacity: 0;
    transition: transform 0.3s ease, opacity 0.3s ease;
  }

  .point-item:active::after {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
  }

  .point-item {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 40px;
    transition: all 0.3s ease;
  }

  .sprint-container {
    margin-top: 20px;
    padding: 16px;
    background: #f5f5f5;
    border-radius: 8px;
  }

  .sprint-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .sprint-stats {
    font-size: 0.9em;
    color: rgba(0, 0, 0, 0.6);
  }
  </style>