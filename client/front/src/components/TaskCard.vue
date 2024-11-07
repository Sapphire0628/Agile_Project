<template>
  <v-container>
    <v-row>
      <v-col cols="8">
        <h3>Tasks</h3>
      </v-col>
      <v-col cols="4" class="text-right">
        <v-btn color="primary" @click="openCreateTaskDialog">+</v-btn>
      </v-col>
    </v-row>
    <v-card class="scroll-box">
      <v-card-text>
        <v-row v-if="tasks.length > 0">
          <v-col v-for="(task, index) in tasks" :key="index" cols="12">
            <v-card>
              <v-card-title>
                {{ task.name }}
              </v-card-title>
              <v-card-subtitle>
                Owner: {{ task.owner }} | Status: {{ task.status }}
              </v-card-subtitle>
              <v-card-text>
                Description: {{ task.description }}
                <div v-if="task.attachments && task.attachments.length > 0">
                  <div>Attachments:</div>
                  <v-list>
                    <v-list-item v-for="(attachment, index) in task.attachments" :key="index">
                      <v-list-item-content>
                        <v-list-item-title>
                          <a :href="attachment" target="_blank">{{ attachment }}</a>
                        </v-list-item-title>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list>
                </div>
              </v-card-text>
              <v-card-actions>
                <v-btn color="primary" text @click="editTask(task, index)">Edit</v-btn>
                <v-btn color="error" text @click="deleteTask(index)">Delete</v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
        <div v-else>
          <v-card>
            <v-card-text>Empty</v-card-text>
          </v-card>
        </div>
      </v-card-text>
    </v-card>
    <v-dialog v-model="showCreateTaskDialog" persistent max-width="500">
      <v-card>
        <v-card-title>{{ editingTaskIndex !== null ? 'Edit Task' : 'Create Task' }}</v-card-title>
        <v-card-text>
          <v-form>
            <v-text-field v-model="newTask.name" label="Task Name" :rules="[v => !!v || 'Task Name is required']" required></v-text-field>
            <v-text-field v-model="newTask.owner" label="Owner" :rules="[v => !!v || 'Owner is required']" required></v-text-field>
            <v-textarea
                v-model="newTask.description"
                label="Description"
                rows="3"
                required
            ></v-textarea>
            <v-text-field
                v-model="newTask.attachmentsUrl"
                label="Attachments URL (comma separated)"
                hint="Enter URLs separated by commas"
            ></v-text-field>
            <v-select
                v-model="newTask.status"
                :items="['new', 'done', 'in progress']"
                label="Status"
            ></v-select>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="editingTaskIndex !== null ? updateTask() : createTask()">
            {{ editingTaskIndex !== null ? 'Update' : 'Create' }}
          </v-btn>
          <v-btn color="secondary" text @click="showCreateTaskDialog = false">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
export default {
  name: 'TaskCard',
  data() {
    return {
      tasks: [],
      showCreateTaskDialog: false,
      editingTaskIndex: null,
      newTask: {
        name: '',
        owner: '',
        description: '',
        attachmentsUrl: '',
        status: 'new',
      },
    };
  },
  methods: {
    openCreateTaskDialog() {
      this.showCreateTaskDialog = true;
      this.editingTaskIndex = null;
    },
    createTask() {
      if (this.newTask.name && this.newTask.owner && this.newTask.description) {
        const attachments = this.newTask.attachmentsUrl
            .split(',')
            .map(url => url.trim())
            .filter(url => url.length > 0);

        this.tasks.push({
          ...this.newTask,
          attachments,
        });

        this.resetNewTask();
        this.showCreateTaskDialog = false;
      }
    },
    editTask(task, index) {
      this.newTask = {
        ...task,
        attachmentsUrl: task.attachments.join(', '),
      };
      this.editingTaskIndex = index;
      this.showCreateTaskDialog = true;
    },
    updateTask() {
      if (this.newTask.name && this.newTask.owner && this.newTask.description) {
        const attachments = this.newTask.attachmentsUrl
            .split(',')
            .map(url => url.trim())
            .filter(url => url.length > 0);

        this.tasks.splice(this.editingTaskIndex, 1, {
          ...this.newTask,
          attachments,
        });

        this.resetNewTask();
        this.showCreateTaskDialog = false;
      }
    },
    deleteTask(index) {
      this.tasks.splice(index, 1);
    },
    resetNewTask() {
      this.newTask = {
        name: '',
        owner: '',
        description: '',
        attachmentsUrl: '',
        status: 'new',
      };
      this.editingTaskIndex = null;
    },
  },
};
</script>

<style scoped>
.scroll-box {
  max-height: 400px;
  overflow-y: auto;
}

.text-right {
  text-align: right;
}
</style>