<template>
  <v-dialog v-model="dialog" max-width="1000px" persistent>
    <v-card class="task-dialog">
      <v-card-title class="d-flex align-center pa-4">
        <span class="text-h6">Task Details</span>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-close" variant="text" @click="dialog = false"></v-btn>
      </v-card-title>

      <v-divider></v-divider>

      <v-card-text class="pa-0">
        <v-row no-gutters style="min-height: 600px;">
          <v-col cols="6" class="border-r">
            <div class="pa-4">
              <v-skeleton-loader v-if="loading" type="article" />
              
              <template v-else>
                <div class="d-flex align-center mb-6" :class="{ 'task-done': taskDetail.status === 'Done' }">
                  <div class="text-h5 font-weight-medium" :class="{ 'task-title-done': taskDetail.status === 'Done' }">
                    #{{ taskId }} {{ taskDetail.name }}
                  </div>
                  <v-chip
                    :color="getStatusColor(taskDetail.status)"
                    class="ml-4"
                    variant="elevated"
                    :class="{ 'chip-done': taskDetail.status === 'Done' }"
                  >
                    {{ taskDetail.status }}
                  </v-chip>
                </div>

                <div class="mb-6 task-description pa-4 rounded bg-grey-lighten-4" 
                  :class="{ 'description-done': taskDetail.status === 'Done' }"
                >
                  <div class="text-subtitle-2 font-weight-medium mb-2">Task Description</div>
                  <div class="text-body-1" :class="{ 'text-grey': taskDetail.status === 'Done' }">
                    {{ taskDetail.description || 'No description' }}
                  </div>
                </div>

                <div class="date-info mb-6 pa-4 rounded bg-grey-lighten-4">
                  <div class="d-flex flex-column">
                    <div class="d-flex align-center mb-3">
                      <v-icon icon="mdi-clock-outline" size="small" color="primary" class="mr-2"></v-icon>
                      <div class="text-subtitle-2 font-weight-medium">Time Schedule</div>
                    </div>
                    <div class="time-info">
                      <div class="time-row mb-2">
                        <span class="text-caption text-grey-darken-1 mr-4">Start Time:</span>
                        <span class="text-body-2 font-weight-medium">
                          {{ formatDateDisplay(taskDetail.created_at) }}
                        </span>
                      </div>
                      <div class="time-row">
                        <span class="text-caption text-grey-darken-1 mr-4">Due Date:</span>
                        <span class="text-body-2 font-weight-medium" :class="getDueDateTextClass(taskDetail.due_date)">
                          {{ formatDateDisplay(taskDetail.due_date) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="d-flex align-center mb-4">
                  <v-icon icon="mdi-account-multiple" class="mr-2"></v-icon>
                  <div class="d-flex align-center flex-grow-1">

                    <div v-for="username in members" :key="username">
                      <v-menu location="top">
                        <template v-slot:activator="{ props }">
                          <v-avatar
                            v-bind="props"
                            size="32"
                            class="assignee-avatar"
                            :color="getAvatarColor(username)"
                          >
                            <span class="text-white">{{ username.charAt(0).toUpperCase() }}</span>
                          </v-avatar>
                        </template>
                        
                        <v-card min-width="150">
                          <v-card-text class="pa-2">
                            <div class="d-flex align-center justify-space-between">
                              <span>{{ username }}</span>
                              <v-btn
                                icon="mdi-delete"
                                size="small"
                                variant="text"
                                color="error"
                                :loading="removingUser === username"
                                @click="removeUser(username)"
                              ></v-btn>
                            </div>
                          </v-card-text>
                        </v-card>
                      </v-menu>
                    </div>

                    <v-menu>
                      <template v-slot:activator="{ props }">
                        <v-btn
                          v-bind="props"
                          icon="mdi-plus"
                          size="small"
                          variant="text"
                          class="ml-2"
                          :loading="updatingAssignee"
                        ></v-btn>
                      </template>
                      
                      <v-list width="200">
                        <v-list-item
                          v-for="member in projectMembers"
                          :key="member.username"
                          @click="updateAssignee(member.username)"
                          :disabled="isUserAssigned(member.username)"
                        >
                          <template v-slot:prepend>
                            <v-avatar size="24" :color="getRoleColor(member.role)">
                              <span class="text-white">{{ member.username.charAt(0).toUpperCase() }}</span>
                            </v-avatar>
                          </template>
                          <v-list-item-title>
                            {{ member.username }}
                            <span class="text-caption">({{ member.role }})</span>
                          </v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                  </div>
                </div>
              </template>
            </div>

            <v-divider></v-divider>

            <div class="pa-4">
              <v-textarea
                v-model="newComment"
                label="Add Comment"
                rows="3"
                variant="outlined"
                hide-details
                class="mb-2"
                :loading="submittingComment"
              ></v-textarea>
              <div class="d-flex justify-end">
                <v-btn
                  color="primary"
                  :loading="submittingComment"
                  :disabled="!newComment.trim()"
                  @click="submitComment"
                >
                  Submit Comment
                </v-btn>
              </div>
            </div>
          </v-col>

          <v-col cols="6" class="comments-section">
            <div class="pa-4">
              <div class="text-h6 mb-4">Comment History</div>
              <v-list v-if="comments.length">
                <v-list-item
                  v-for="comment in comments"
                  :key="comment.comment_id"
                  class="mb-4"
                >
                  <template v-slot:prepend>
                    <v-avatar size="36" class="mr-3" :color="getAvatarColor(comment.username)">
                      <span class="text-white">{{ comment.username?.charAt(0).toUpperCase() }}</span>
                    </v-avatar>
                  </template>
                  <v-list-item-title>
                    <div class="d-flex justify-space-between align-center">
                      <span class="font-weight-medium">{{ comment.username }}</span>
                      <div class="d-flex align-center">
                        <span class="text-caption text-grey mr-2">{{ formatDate(comment.created_at) }}</span>
                        <v-btn
                          icon="mdi-close"
                          size="x-small"
                          variant="text"
                          color="grey"
                          :loading="deletingCommentId === comment.comment_id"
                          @click="handleDeleteComment(comment.comment_id)"
                        ></v-btn>
                      </div>
                    </div>
                  </v-list-item-title>
                  <v-list-item-subtitle class="mt-2 text-wrap">
                    {{ comment.comment }}
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
              <div v-else class="text-center text-grey-darken-1 mt-4">
                No comments yet
              </div>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import { ref, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { getTasks, updateTask } from '@/api/task'
import { getTaskComments, addComment, deleteComment } from '@/api/comment'
import { format } from 'date-fns'
import { getProjectMembers } from '@/api/project'

export default {
  name: 'TaskCard',
  props: {
    taskId: {
      type: [Number, String],
      required: true
    },
    projectId: {
      type: [Number, String],
      required: true
    },
    modelValue: {
      type: Boolean,
      default: false
    }
  },

  setup(props, { emit }) {
    const toast = useToast()
    const dialog = ref(false)
    const loading = ref(false)
    const submittingComment = ref(false)
    const taskDetail = ref({})
    const comments = ref([])
    const newComment = ref('')
    const members = ref([])
    const canEdit = ref(true)
    const updatingAssignee = ref(false)
    const projectMembers = ref([])
    const selectedAssignees = ref([])
    const removingUser = ref(null)
    const deletingCommentId = ref(null)

    watch(() => props.modelValue, (val) => {
      dialog.value = val
      if (val) {
        fetchTaskDetail()
        fetchComments()
        fetchMembers()
      }
    })

    watch(dialog, (val) => {
      emit('update:modelValue', val)
      if (!val) {
        newComment.value = ''
      }
    })

    const isUserAssigned = (username) => {
      return taskDetail.value.members?.some(member => member.username === username)
    }

    const fetchTaskDetail = async () => {
      loading.value = true
      try {
        const response = await getTasks({
          task_id: props.taskId,
          project_id: props.projectId
        })
        taskDetail.value = response.data.task
        members.value = response.data.member || []
      } catch (error) {
        toast.error('Failed to get task details')
      } finally {
        loading.value = false
      }
    }

    const fetchMembers = async () => {
      try {
        const response = await getProjectMembers({'project_id':props.projectId})
        projectMembers.value = response.data.users.map(user => ({
          username: user.name,
          role: user.role,
        }))
        console.log(projectMembers.value)
      } catch (error) {
        toast.error('Failed to get project members')
      }
    }

    const fetchComments = async () => {
      try {
        const response = await getTaskComments(props.taskId)
        comments.value = response.data.map(comment => ({
          comment_id: comment.comment_id,
          comment: comment.comment,
          created_at: comment.created_at,
          username: comment['username:']
        }))
      } catch (error) {
        toast.error('Failed to get comments')
      }
    }

    const submitComment = async () => {
      if (!newComment.value.trim()) return

      submittingComment.value = true
      try {
        console.log(newComment.value)
        await addComment({
          task_id: props.taskId,
          comment: newComment.value
        })
        newComment.value = ''
        await fetchComments()
        toast.success('Comment submitted successfully')
      } catch (error) {
        toast.error('Failed to submit comment')
      } finally {
        submittingComment.value = false
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

    const formatDate = (date) => {
      return format(new Date(date), 'yyyy-MM-dd HH:mm')
    }

    const getAvatarColor = (name) => {
      const colors = [
        'primary',
        'success',
        'info',
        'warning',
        'error',
        'purple',
        'indigo',
        'deep-purple',
        'cyan',
        'teal'
      ]
      const charSum = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
      return colors[charSum % colors.length]
    }

    const updateAssignee = async (newAssigneeId) => {
      updatingAssignee.value = true
      try {
        await updateTask({
          task_id: props.taskId,
          user: {users:[newAssigneeId], type: 'add'}
        })
        toast.success('Assignee updated successfully')
        await fetchTaskDetail() 
      } catch (error) {
        toast.error('Failed to update assignee')
        await fetchTaskDetail()
      } finally {
        updatingAssignee.value = false
      }
    }

    const removeUser = async (username) => {
      removingUser.value = username
      try {
        await updateTask({
          task_id: props.taskId,
          user: {users:[username], type: 'remove'}
        })
        toast.success('Assignee removed successfully')
        await fetchTaskDetail()
      } catch (error) {
        toast.error('Failed to remove assignee')
      } finally {
        removingUser.value = null
      }
    }

    const formatDateDisplay = (date) => {
      if (!date) return 'Not set'
      return format(new Date(date), 'yyyy-MM-dd')
    }

    const getDueDateColor = (dueDate) => {
      if (!dueDate) return 'grey'
      const today = new Date()
      const due = new Date(dueDate)
      if (due < today) return 'error'
      if (due - today < 3 * 24 * 60 * 60 * 1000) return 'warning' 
      return 'success'
    }

    const getDueDateTextClass = (dueDate) => {
      if (!dueDate) return ''
      const today = new Date()
      const due = new Date(dueDate)
      if (due < today) return 'text-error'
      if (due - today < 3 * 24 * 60 * 60 * 1000) return 'text-warning'
      return ''
    }

    const getRoleColor = (role) => {
      const colors = {
        'Programmer': '#2196F3',
        'Tester': '#4CAF50',
        'UI Designer': '#FF9800',
        'DevOps engineer': '#E91E63',
        'Project manager': '#00BCD4'
      }
      return colors[role] || 'grey'
    }

    const handleDeleteComment = async (commentId) => {
      deletingCommentId.value = commentId
      try {
        await deleteComment({comment_id: commentId} )
        await fetchComments()
        toast.success('Comment deleted successfully')
      } catch (error) {
        toast.error('Failed to delete comment')
      } finally {
        deletingCommentId.value = null
      }
    }

    return {
      dialog,
      loading,
      taskDetail,
      comments,
      newComment,
      members,
      canEdit,
      submittingComment,
      submitComment,
      getStatusColor,
      formatDate,
      updatingAssignee,
      updateAssignee,
      getAvatarColor,
      formatDateDisplay,
      getDueDateColor,
      getDueDateTextClass,
      fetchMembers,
      projectMembers,
      selectedAssignees,
      getRoleColor,
      isUserAssigned,
      removingUser,
      removeUser,
      deletingCommentId,
      handleDeleteComment
    }
  }
}
</script>

<style scoped>
.task-dialog {
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.border-r {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
}

.comments-section {
  max-height: calc(80vh - 64px);
  overflow-y: auto;
}

.max-width-200 {
  max-width: 200px;
}

.text-wrap {
  white-space: pre-wrap;
}

.assignee-avatars {
  gap: 4px;
}

.assignee-avatar {
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.assignee-avatar:not(:first-child) {
  margin-left: -8px;
}

.task-description {
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.date-info {
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.time-info {
  padding-left: 24px;
}

.time-row {
  display: flex;
  align-items: center;
}

.time-block,
.gap-4 {
  display: none;
}

.comments-section .v-list-item {
  width: 100%;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 12px;
}

.comments-section .v-list {
  width: 100%;
}

.comments-section .v-btn {
  opacity: 0.7;
  transition: opacity 0.2s;
}

.comments-section .v-btn:hover {
  opacity: 1;
}

.task-done {
  opacity: 0.8;
}

.task-title-done {
  color: #9e9e9e;
  text-decoration: line-through;
}

.description-done {
  background-color: #fafafa !important;
  border-color: rgba(0, 0, 0, 0.03) !important;
}

.chip-done {
  opacity: 0.7;
}

.text-grey {
  color: #9e9e9e !important;
}

.task-done .comments-section .v-list-item {
  opacity: 0.8;
  background: #fafafa;
}
</style>