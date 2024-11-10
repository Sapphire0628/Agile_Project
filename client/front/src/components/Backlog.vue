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
  
      <v-container class="task-container">
        <Draggable 
          v-model="filteredTasks" 
          group="tasks"
          item-key="task_id"
          @end="onDragEnd"
          :sort="false"
        >
          <template #item="{ element: task, index }">
            <v-card 
              :key="task.task_id" 
              class="task-card mb-4"
              elevation="1"
              :data-task-id="task.task_id"
            >
              <v-card-text>
                <div class="d-flex justify-space-between align-center">
                  <div class="task-name text-h6">
                    <span class="task-id">#{{ index + 1 }}</span>
                    {{ task.task_name }}
                  </div>
                  
                  <div class="task-meta d-flex align-center">
                    <v-menu
                      v-model="task.showStatusMenu"
                      :close-on-content-click="false"
                      location="bottom"
                      :offset="8"
                      min-width="200"
                    >
                      <template v-slot:activator="{ props }">
                        <v-chip
                          size="small"
                          class="mr-4"
                          :color="getStatusColor(task.status)"
                          v-bind="props"
                          style="cursor: pointer"
                        >
                          {{ task.status}}
                        </v-chip>
                      </template>
                      <v-card>
                        <v-list>
                          <v-list-item
                            v-for="status in statusOptions"
                            :key="status"
                            :title="status"
                            @click="updateTaskStatus(task.task_id, status); task.showStatusMenu = false"
                          >
                          </v-list-item>
                        </v-list>
                      </v-card>
                    </v-menu>
                    <v-menu
                      v-model="task.showPointsMenu"
                      :close-on-content-click="false"
                      location="bottom"
                      :offset="8"
                      min-width="300"
                    >
                      <template v-slot:activator="{ props }">
                        <v-chip
                          size="small"
                          color="primary"
                          v-bind="props"
                          style="cursor: pointer"
                        >
                          {{ task.priority ? `${task.priority} points` : '0 points' }}
                        </v-chip>
                      </template>
                      <v-card>
                        <div class="points-container">
                          <div
                            v-for="point in storyPointsWithDesc"
                            :key="point.value"
                            class="point-item"
                            :class="{ 'selected': task.priority === point.value }"
                            @click="updateTaskPoints(task.task_id, point.value); task.showPointsMenu = false"
                          >
                            <v-tooltip location="top">
                              <template v-slot:activator="{ props }">
                                <div v-bind="props">{{ point.value }}</div>
                              </template>
                              {{ point.description }}
                            </v-tooltip>
                          </div>
                        </div>
                      </v-card>
                    </v-menu>
                    <v-menu location="bottom end">
                      <template v-slot:activator="{ props }">
                        <v-btn
                          icon="mdi-dots-vertical"
                          size="small"
                          variant="text"
                          v-bind="props"
                      ></v-btn>
                    </template>
                    <v-list>
                      <v-list-item
                        @click="handleDeleteTask(task.task_id)"
                        prepend-icon="mdi-delete"
                        title="删除"
                            color="error"
                          ></v-list-item>
                        </v-list>
                      </v-menu>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </template>
        </Draggable>
      </v-container>

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
                <v-form ref="form" @submit.prevent>
                  <v-text-field
                    v-model="newTask.task_name"
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
                    v-model="newTask.priority"
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
                        :class="{ 'selected': newTask.priority === point.value }"
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
              :loading="isLoading"
              @click="createTask"
              v-text="'Create'"
            ></v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </template>
  
  <script>
  import { ref, onMounted, computed } from 'vue'
  import { useRouter } from 'vue-router'
  import Draggable from 'vuedraggable'
  import { getTasks, addTask, updateTask, deleteTask } from '@/api/task'
  import { updateSprintTask } from '@/api/sprint'
  import { useToast } from 'vue-toastification'
  
  export default {
    name: 'Backlog',
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
    expose: ['fetchTasks'],
    setup(props) {
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
      const toast = useToast()

      const statusOptions = [
        'Not start',
        'Started',
        'Testing',
        'Review',
        'Done'
      ]
  
      const storyPointOptions = [ 0,  1, 2, 3, 5, 8, 10, 13, 20, 40]
  
      const onDragEnd = async (evt) => {
        const { from, to } = evt
        if (from === to) return 

        const taskId = evt.item.dataset.taskId
        const sprintId = to?.dataset?.sprintId
        const ifFromBacklog = from.classList.contains('task-container')
        if(taskId && sprintId && !ifFromBacklog){
          try{
            await updateSprintTask({tasks:[taskId], round:sprintId, type:'add', project_id:props.projectId})
            await fetchTasks()
            toast.success('任务移动成功')
          } catch (error) {
            console.error('Failed to update task sprint:', error)
            toast.error('任务移动失败')
            await fetchTasks()
          }
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
        task_name: '',
        description: '',
        status: 'Not start',
        priority: null,
        project_id: props.projectId
      })

      const resetForm = () => {
        newTask.value = {
          task_name: '',
          description: '',
          status: 'Not start',
          priority: null,
          project_id: props.projectId
        }
        if (form.value) {
          form.value.resetValidation()
        }
      }
  
      const createTask = async () => {
        if(!form.value){
            toast.error('表单未初始化')
            return
        }
        const { valid } = await form.value.validate()
        if(!valid){
            toast.error('请填写任务名')
            return
        }
        try {
          isLoading.value = true
          console.log(props)
          await addTask(newTask.value)
          showNewTaskDialog.value = false
          resetForm()
          await fetchTasks()
        } catch (error) {
          console.error('Failed to create task:', error)
 
        } finally {
          isLoading.value = false
        }
      }
      const fetchTasks = async () => {
        try{
            const fetchtasks = await getTasks({'project_id':props.projectId})
            tasks.value = fetchtasks.data.tasks || []
            console.log(tasks.value)
        } catch (error) {
            console.error('Failed to fetch tasks:', error)
            toast.error('Failed to fetch tasks')
            tasks.value = []
        }
      }
      const selectPoints = (point) => {
        newTask.value.priority = point
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
        { value: 0, description: 'no priority' },
        { value: 1, description: 'very easy' },
        { value: 2, description: 'normal task' },
        { value: 3, description: 'medium task' },
        { value: 5, description: 'complex task' },
        { value: 8, description: 'hard task' },
        { value: 13, description: 'large task' },
        { value: 20, description: 'huge task, consider splitting' },
        { value: 40, description: 'massive task, must split' }
      ]

      const totalStoryPoints = computed(() => {
        return tasks.value.reduce((sum, task) => sum + (Number(task.priority) || 0), 0)
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

      const filteredTasks = computed(() => {
        if(!search.value){
          return tasks.value
        }
        return tasks.value.filter(task =>
          task.task_name.toLowerCase().includes(search.value.toLowerCase()) ||
          String(task.task_id).includes(search.value.toLowerCase())
        )
      })

      const updateTaskStatus = async (taskId, newStatus) => {
        try {

          await updateTask({task_id:taskId, status: newStatus })

          const task = tasks.value.find(t => t.task_id === taskId)
          if (task) {
            task.status = newStatus
          }
          toast.success('状态更新成功')
        } catch (error) {
          console.error('Failed to update task status:', error)
          toast.error('状态更新失败')
        }
      }

      const updateTaskPoints = async (taskId, newPoints) => {
        try {

          await updateTask({task_id:taskId, priority: newPoints })

          const task = tasks.value.find(t => t.task_id === taskId)
          if (task) {
            task.priority = newPoints
          }
          toast.success('分数更新成功')
        } catch (error) {
          console.error('Failed to update task points:', error)
          toast.error('分数更新失败')
        }
      }

      const handleDeleteTask = async (taskId) => {
        try {
          await deleteTask({task_id:taskId})
          await fetchTasks()
          toast.success('任务删除成功')
        } catch (error) {
          console.error('Failed to delete task:', error)
          toast.error('任务删除失败')
        }
      }

      onMounted(()=>{
        fetchTasks()
      })

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
        moveTaskToSprint,
        updateTaskStatus,
        updateTaskPoints,
        handleDeleteTask,
        form,
        getStatusColor,
        fetchTasks
      }
    }
  }

  </script>
  
  <style scoped>
  .backlog {
    padding: 24px;
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

  .points-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 4px;
    padding: 8px;
    position: relative;
    z-index: 1100;
  }

  .point-item {
    padding: 8px;
    text-align: center;
    cursor: pointer;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 40px;
    transition: all 0.3s ease;
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

  .task-container {
    max-width: 900px;
    margin: 0 auto;
  }

  .task-card {
    border-radius: 8px;
  }

  .task-name {
    font-weight: 500;
    color: rgba(0, 0, 0, 0.87);
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .task-id {
    color: #666;
    font-weight: 400;
    font-size: 0.9em;
  }

  .task-meta {
    display: flex;
    align-items: center;
    gap: 8px; 
  }

  .task-actions {
    opacity: 0.5;
    transition: opacity 0.2s ease;
  }

  .task-card:hover .task-actions {
    opacity: 1;
  }

  .v-list-item {
    min-height: 40px;
  }
  </style>