<template>
  <v-navigation-drawer
    permanent
    expand-on-hover
    width="200"
  >
    <v-list class="py-4">
      <v-list-item
        prepend-icon="mdi-account-group"
        title="Team"
        value="team"
        :active="isTeamRoute"
        @click="navigateToTeam"
      >
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export default {
  setup() {
    const route = useRoute()
    const router = useRouter()

    const isTeamRoute = computed(() => {
      return route.name === 'Team'
    })

    const navigateToTeam = () => {
      const projectId = route.params.id
      router.push(`/project/${projectId}/team`)
    }

    return {
      isTeamRoute,
      navigateToTeam
    }
  }
}
</script>

<style scoped>
.sidebar {
  background: #f8f9fa;
  border-right: 1px solid rgba(var(--v-border-color), 0.12);
}

:root[data-theme="dark"] .sidebar {
  background: #1e1e1e;
}
</style>