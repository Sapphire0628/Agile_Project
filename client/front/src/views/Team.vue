<template>
  <v-layout>
    <Header />
    <SideBar />
    <v-main>
      <v-container fluid>
        <div class="team-section">
          <v-card flat class="mb-6">
            <v-toolbar flat color="transparent" class="px-4">
              <v-toolbar-title class="text-h5">Team Members</v-toolbar-title>
              <v-spacer></v-spacer>
              <v-btn
                icon
                color="error"
                variant="text"
                :disabled="selectedMembers.length === 0"
                @click="showDeleteConfirmation = true"
                class="mr-2"
              >
                <v-icon>mdi-delete</v-icon>
              </v-btn>
              <v-btn
                icon
                color="primary"
                variant="text"
                @click="showAddMemberDialog = true"
              >
                <v-icon>mdi-plus</v-icon>
              </v-btn>
            </v-toolbar>
          </v-card>

          <v-card flat>
            <v-list>
              <v-list-item
                v-for="member in members"
                :key="member.username"
                :class="{'selected': selectedMembers.includes(member)}"
                @click="toggleMemberSelection(member)"
                class="member-item"
                density="compact"
              >
                <template v-slot:prepend>
                  <v-avatar :color="getRandomColor(member.username)" size="36" class="mr-3">
                    <span class="text-subtitle-2 white--text">
                      {{ member.username ? member.username.charAt(0).toUpperCase() : '?' }}
                    </span>
                  </v-avatar>
                </template>

                <v-list-item-title class="text-subtitle-1">
                  {{ member.username }}
                </v-list-item-title>

                <template v-slot:append>
                  <v-checkbox-btn
                    v-model="selectedMembers"
                    :value="member"
                    hide-details
                    density="compact"
                    class="ml-2"
                  ></v-checkbox-btn>
                </template>
              </v-list-item>
            </v-list>
          </v-card>
        </div>

        <v-dialog v-model="showAddMemberDialog" max-width="500px">
          <v-card>
            <v-card-title>Add Team Member</v-card-title>
            <v-card-text>
              <v-text-field
                v-model="newMemberUsername"
                label="Username"
                required
                :error-messages="usernameError"
                @keyup.enter="addMember"
              ></v-text-field>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                color="grey-darken-1"
                variant="text"
                @click="closeAddMemberDialog"
              >
                Cancel
              </v-btn>
              <v-btn
                color="primary"
                variant="text"
                @click="addMember"
                :loading="addingMember"
              >
                Add
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <v-dialog v-model="showDeleteConfirmation" max-width="500px">
          <v-card>
            <v-card-title>Delete Members</v-card-title>
            <v-card-text>
              Are you sure you want to delete {{ selectedMembers.length }} selected member(s)?
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                color="grey-darken-1"
                variant="text"
                @click="showDeleteConfirmation = false"
              >
                Cancel
              </v-btn>
              <v-btn
                color="error"
                variant="text"
                @click="deleteSelectedMembers"
                :loading="deletingMembers"
              >
                Delete
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-container>
    </v-main>
  </v-layout>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Header from '@/components/Header.vue'
import SideBar from '@/components/SideBar.vue'
import { getProjectMembers, manageProjectMember } from '@/api/project'

export default {
  name: 'TeamView',
  components: {
    Header,
    SideBar
  },
  setup() {
    const route = useRoute()
    const projectId = route.params.id


    const headers = [
      { title: 'Avatar', key: 'avatar', sortable: false, width: '80px' },
      { title: 'Username', key: 'username', width: '200px' }
    ]


    const members = ref([])
    const loading = ref(false)
    const selectedMembers = ref([])
    const showAddMemberDialog = ref(false)
    const showDeleteConfirmation = ref(false)
    const newMemberUsername = ref('')
    const usernameError = ref('')
    const addingMember = ref(false)
    const deletingMembers = ref(false)

    const getRandomColor = (username) => {
      if (!username) return '#2196F3'
      const colors = [
        '#2196F3', '#4CAF50', '#FF9800', '#E91E63',
        '#9C27B0', '#00BCD4', '#009688', '#F44336'
      ]
      const hash = username.split('').reduce((acc, char) => {
        return char.charCodeAt(0) + ((acc << 5) - acc)
      }, 0)
      return colors[Math.abs(hash) % colors.length]
    }


    const fetchMembers = async () => {
      try {
        loading.value = true
        const response = await getProjectMembers({'project_id':projectId})
        members.value = response.data.users.map(username => ({
          username: username
        }))
        console.log(members.value)
      } catch (error) {
        console.error('Failed to fetch members:', error)
      } finally {
        loading.value = false
      }
    }

    const addMember = async () => {
      if (!newMemberUsername.value.trim()) {
        usernameError.value = 'Username is required'
        return
      }

      try {
        addingMember.value = true
        const data = {'project_id':projectId,'type':'add','users':[newMemberUsername.value]}
        await manageProjectMember(data)
        await fetchMembers()
        closeAddMemberDialog()
      } catch (error) {
        console.error('Failed to add member:', error)
        usernameError.value = 'Failed to add member'
      } finally {
        addingMember.value = false
      }
    }

    const deleteSelectedMembers = async () => {
      try {
        deletingMembers.value = true
        const data = {'project_id':projectId,'type':'remove','users':selectedMembers.value.map(member => member.username)}
        await manageProjectMember(data)
        await fetchMembers()
        showDeleteConfirmation.value = false
        selectedMembers.value = []
      } catch (error) {
        console.error('Failed to delete members:', error)
      } finally {
        deletingMembers.value = false
      }
    }

    const closeAddMemberDialog = () => {
      showAddMemberDialog.value = false
      newMemberUsername.value = ''
      usernameError.value = ''
    }

    const toggleMemberSelection = (member) => {
      const index = selectedMembers.value.indexOf(member)
      if (index === -1) {
        selectedMembers.value.push(member)
      } else {
        selectedMembers.value.splice(index, 1)
      }
    }

    onMounted(() => {
      fetchMembers()
    })

    return {
      headers,
      members,
      loading,
      selectedMembers,
      showAddMemberDialog,
      showDeleteConfirmation,
      newMemberUsername,
      usernameError,
      addingMember,
      deletingMembers,
      getRandomColor,
      addMember,
      deleteSelectedMembers,
      closeAddMemberDialog,
      toggleMemberSelection
    }
  }
}
</script>

<style scoped>
.team-section {
  padding: 24px;
}

.member-item {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
  transition: all 0.2s ease;
  min-height: 56px;
  padding: 0 16px;
}

.member-item :deep(.v-list-item__content) {
  padding: 8px 0;
}

.member-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.member-item.selected {
  background-color: rgba(var(--v-theme-primary), 0.1);
}

.member-item:last-child {
  border-bottom: none;
}
</style>