<template>
  <v-layout>
    <Header />
    <SideBar />
    <v-main>
      <v-container fluid>
        <div class="team-section">
          <v-row class="mb-6">
            <v-col cols="12" sm="6">
              <v-card class="stats-card">
                <v-card-text class="text-center">
                  <div class="text-h4 mb-2">{{ members.length }}</div>
                  <div class="text-subtitle-1">团队成员</div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" sm="6">
              <v-card class="stats-card">
                <v-card-text class="text-center">
                  <div class="text-h4 mb-2">{{ selectedMembers.length }}</div>
                  <div class="text-subtitle-1">已选成员</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <v-card flat class="mb-6">
            <v-toolbar flat color="transparent" class="px-4">
              <v-toolbar-title class="text-h4 font-weight-bold">Team Members</v-toolbar-title>
              <v-spacer></v-spacer>
              <v-text-field
                v-model="search"
                prepend-inner-icon="mdi-magnify"
                label="搜索成员"
                single-line
                hide-details
                density="compact"
                class="mr-4"
                style="max-width: 300px"
              ></v-text-field>
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

          <div class="pa-4">
            <div class="members-container">
              <v-row class="ma-0">
                <v-col
                  v-for="member in filteredMembers"
                  :key="member.username"
                  cols="12"
                  sm="6"
                  md="4"
                  lg="3"
                  class="pa-2"
                >
                  <v-card
                    :class="{'member-card': true, 'selected': selectedMembers.includes(member)}"
                    @click="toggleMemberSelection(member)"
                    elevation="2"
                  >
                    <v-card-text class="pa-4">
                      <div class="d-flex align-center">
                        <v-avatar :color="getRandomColor(member.username)" size="48" class="mr-3">
                          <span class="text-h6 white--text">
                            {{ member.username ? member.username.charAt(0).toUpperCase() : '?' }}
                          </span>
                        </v-avatar>
                        <div class="member-info flex-grow-1">
                          <div class="text-h6 font-weight-medium">{{ member.username }}</div>
                          <div class="role-chip" @click.stop>
                            <v-menu
                              v-model="member.showRoleMenu"
                              :close-on-content-click="false"
                              location="bottom"
                            >
                              <template v-slot:activator="{ props }">
                                <v-chip
                                  :color="ROLE_COLORS[member.role]"
                                  text-color="white"
                                  size="small"
                                  v-bind="props"
                                >
                                  {{ ROLES.find(r => r.value === member.role)?.text || member.role }}
                                </v-chip>
                              </template>
                              
                              <v-list>
                                <v-list-item
                                  v-for="role in ROLES"
                                  :key="role.value"
                                  :value="role.value"
                                  @click="updateMemberRole(member, role.value)"
                                  class="role-list-item"
                                  :style="{
                                    '--hover-color': `${role.color}15`
                                  }"
                                >
                                  <template v-slot:prepend>
                                    <v-icon :color="role.color" size="24">
                                      {{ role.icon }}
                                    </v-icon>
                                  </template>
                                  <v-list-item-title>{{ role.text }}</v-list-item-title>
                                </v-list-item>
                              </v-list>
                            </v-menu>
                          </div>
                        </div>
                        <v-checkbox-btn
                          v-model="selectedMembers"
                          :value="member"
                          hide-details
                          density="compact"
                          @click.stop
                        ></v-checkbox-btn>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </div>
          </div>
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
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import Header from '@/components/Header.vue'
import SideBar from '@/components/SideBar.vue'
import { getProjectMembers, manageProjectMember } from '@/api/project'
import { useToast } from 'vue-toastification'

const ROLES = [
  { 
    value: 'Programmer', 
    text: 'Programmer', 
    color: '#2196F3',
    icon: 'mdi-code-braces' 
  },
  { 
    value: 'Tester', 
    text: 'Tester', 
    color: '#4CAF50',
    icon: 'mdi-test-tube' 
  },
  { 
    value: 'UI Designer', 
    text: 'UI Designer', 
    color: '#FF9800',
    icon: 'mdi-palette' 
  },
  { 
    value: 'DevOps engineer', 
    text: 'DevOps engineer', 
    color: '#E91E63',
    icon: 'mdi-cog-transfer' 
  },
]

const ROLE_COLORS = {
  'Programmer': '#2196F3',
  'Tester': '#4CAF50',
  'UI Designer': '#FF9800',
  'DevOps engineer': '#E91E63',
  'Project manager': '#00BCD4'
}

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

    const toast = useToast()
    const members = ref([])
    const loading = ref(false)
    const selectedMembers = ref([])
    const showAddMemberDialog = ref(false)
    const showDeleteConfirmation = ref(false)
    const newMemberUsername = ref('')
    const usernameError = ref('')
    const addingMember = ref(false)
    const deletingMembers = ref(false)
    const updatingRole = ref(false)
    const showRoleMenu = ref(false)
    const selectedMemberForRole = ref(null)

    const search = ref('')

    const filteredMembers = computed(() => {
      return members.value.filter(member =>
        member.username.toLowerCase().includes(search.value.toLowerCase())
      )
    })

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
        members.value = response.data.users.map(user => ({
          username: user.name,
          role: user.role,
          showRoleMenu: false
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
        const data = {'project_id':parseInt(projectId),'type':'add','users':[{name:newMemberUsername.value}]}
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
        const data = {'project_id':parseInt(projectId),'type':'remove','users':selectedMembers.value.map(member => ({name:member.username}))}
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

    const updateMemberRole = async (member, newRole) => {
      try {
        updatingRole.value = true
        const data = {
          'project_id': parseInt(projectId),
          'type': 'update',
          'users': [{'name': member.username, 'role': newRole}]
        }
        await manageProjectMember(data)
        await fetchMembers()
        toast.success('Role updated successfully')
      } catch (error) {
        console.error('Failed to update role:', error)
        toast.error('Failed to update role')
      } finally {
        updatingRole.value = false
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
      toggleMemberSelection,
      search,
      filteredMembers,
      ROLES,
      ROLE_COLORS,
      updateMemberRole,
      showRoleMenu,
      selectedMemberForRole,
    }
  }
}
</script>

<style scoped>
.team-section {
  padding: 24px;
  background-color: rgb(var(--v-theme-background));
}

.members-container {
  max-height: 600px;
  overflow-y: auto;
  padding-right: 8px;
}

.members-container::-webkit-scrollbar {
  width: 6px;
}

.members-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.members-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.members-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.member-card {
  transition: all 0.2s ease;
  cursor: pointer;
  border: 2px solid transparent;
}

.member-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}

.member-card.selected {
  border-color: var(--v-theme-primary);
  background-color: rgba(var(--v-theme-primary), 0.05);
}

.member-info {
  overflow: hidden;
}

.member-info .text-h6 {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.role-chip {
  display: inline-block;
  margin-top: 4px;
  cursor: pointer;
}

.role-list-item {
  border-radius: 8px;
  margin: 4px 8px;
  transition: all 0.3s ease;
}

.role-list-item:hover {
  background-color: var(--hover-color) !important;
}

.v-list-item-title {
  font-weight: 500;
}
</style>