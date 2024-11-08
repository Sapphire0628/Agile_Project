<template>
  <v-card variant="outlined" class="project-card mb-3 rounded-lg" elevation="0" hover>
    <div class="d-flex pa-4 clickable" @click="handleCardClick">
      <!-- 左侧头像部分 -->
      <v-avatar
        size="50"
        class="mr-4 project-avatar flex-shrink-0"
        :color="`rgb(${getRandomColor()})`"
      >
        <span class="text-h6 font-weight-medium white--text">
          {{ project.project_name.charAt(0).toUpperCase() }}
        </span>
      </v-avatar>
      
      <!-- 右侧内容部分 -->
      <div class="flex-grow-1 min-width-0">
        <div class="d-flex justify-space-between align-center mb-3">
          <div class="d-flex flex-column flex-grow-1 min-width-0 mr-4">
            <h3 class="text-h5 font-weight-medium mb-1 text-truncate">{{ project.project_name }}</h3>
            <div class="text-caption text-grey">
              <v-icon size="small" class="mr-1">mdi-clock-outline</v-icon>
              {{ formatDate(project.created_at) }}
            </div>
          </div>
          <!-- 删除按钮 -->
          <v-btn
          icon="mdi-delete"
          variant="tonal"   
          size="small"
          color="error"
          class="delete-btn flex-shrink-0"
            @click.stop="confirmDelete"
            :ripple="false" 
          >
          </v-btn>
        </div>
        
        <!-- 项目描述 -->
        <p class="text-body-2 text-grey description-text" v-if="project.description">
          {{ project.description }}
        </p>
      </div>
    </div>
    

    <!-- 确认删除对话框 -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">
          Delete Project
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete project "{{ project.project_name }}"?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey"
            variant="text"
            @click="showDeleteDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            @click="deleteProject"
            :loading="isDeleting"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { deleteProject } from '@/api/project'

export default {
  name: 'ProjectCard',
  props: {
    project: {
      type: Object,
      required: true,
      validator: (obj) => {
        console.log(obj)
        return typeof obj.project_name === 'string' && obj.project_name.length > 0
      }
    }
  },
  mounted(){
    console.log('ProjectCard mounted, project:',this.project)
  },
  data() {
    return {
      showDeleteDialog: false,
      isDeleting: false
    }
  },
  methods: {
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },
    getRandomColor() {
      const colors = [
        '25, 118, 210',
        '56, 142, 60',
        '211, 47, 47',
        '123, 31, 162',
        '245, 124, 0',
        '0, 151, 167'
      ];
      return colors[Math.floor(Math.random() * colors.length)];
    },
    async deleteProject() {
      try {
        this.isDeleting = true
        await deleteProject({'project_id': this.project.project_id,
            'owner_id': this.project.owner_id
        })
        this.$emit('project-deleted', this.project.project_id)
        this.showDeleteDialog = false
      } catch (error) {
        console.error('Failed to delete project:', error)
      } finally {
        this.isDeleting = false
      }
    },
    handleCardClick(){
      this.$router.push(`/project/${this.project.project_id}`)
    },
    confirmDelete() {
      this.showDeleteDialog = true
    }
  }
}
</script>

<style scoped>
.project-card {
  transition: all 0.3s ease;
  border: 1px solid rgba(var(--v-border-color), 0.12) !important;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
}

.project-avatar {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.text-grey {
  color: rgba(0, 0, 0, 0.6) !important;
}

.description-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: break-word;
  margin-bottom: 0;
}

.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.v-chip {
  font-weight: 500;
}

.text-h5 {
  line-height: 1.4;
  font-size: 1.25rem !important;
}

.text-caption {
  line-height: 1.4;
  display: flex;
  align-items: center;
}

.delete-btn {
  opacity: 1;
  transition: all 0.2s ease;
  margin-left: 8px;
}

.delete-btn:hover {
  transform: scale(1.1);
}

.min-width-0 {
  min-width: 0;
} 

.flex-shrink-0 {
  flex-shrink: 0;
}
</style>