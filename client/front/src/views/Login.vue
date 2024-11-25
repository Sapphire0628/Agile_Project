<template>
  <div class="login-container">
    <v-card class="corner" width="500px">
      <v-toolbar color="primary">
        <v-toolbar-title>Login</v-toolbar-title>
      </v-toolbar>
      <v-container fluid>
        <v-card-text>
          <v-form @keyup.enter.native="login" v-model="valid" ref="form" lazy-validation>
            <v-text-field
            v-model="username"
            label="Username"
            :rules="usernameRules"
            :counter="10"
            required
            prepend-inner-icon="mdi mdi-account"
          ></v-text-field>
            <v-text-field
              v-model="password"
              :rules="passwordRules"
              label="Password"
              required
              prepend-inner-icon="mdi mdi-lock"
            ></v-text-field>
          </v-form>
            <v-card-actions class="d-flex justify-center">
              <v-btn variant="outlined" color="primary" :disabled="!valid" @click="login">Login</v-btn>
              <v-btn variant="outlined" @click="goToRegister">No account? Register</v-btn>
            </v-card-actions>
        </v-card-text>
      </v-container>
    </v-card>
  </div>
</template>

<script>
import { useToast } from 'vue-toastification'

export default {
  setup() {
    const toast = useToast()
    return { toast }
  },
  data:() => ({
      valid: true,
      username: '',
      usernameRules: [
      v => !!v || 'Username cannot be empty',
      v => (v&&v.length <= 10) || 'Username cannot exceed 10 characters'
      ],
      password: '',
      passwordRules: [
      v => !!v || 'Password is required',
        v => v.length >= 6 || 'Password must be at least 6 characters',
        v => /[A-Z]/.test(v) || 'Password must contain at least one uppercase letter',
        v => /[a-z]/.test(v) || 'Password must contain at least one lowercase letter',
        v => /[0-9]/.test(v) || 'Password must contain at least one number'
      ]
  }),

  methods: {
    login() {
      if (this.$refs.form.validate()) {
          this.$axios.post('https://b06d2e0d-a156-474f-adfa-a53fade93306-00-392iabnynab1k.pike.replit.dev/auth/login', {
            username: this.username,
            password: this.password,
          })
          .then(response => {
            const token = response.data.token
            this.$store.dispatch('user/login', token)
            this.$store.dispatch('user/setUsername', this.username)
            this.toast.success('Login successful')
            const redirectPath = this.$route.query.redirect || '/home'
            this.$router.push(redirectPath)
            console.log('Login successful')
          })
          .catch(() => {
            this.toast.error('Login failed')
            console.log('Login failed')
          })
        }
    },
    goToRegister() {
      this.$router.push('/register');
    },
    forgotPassword() {
    }
  }
}

</script>

<style scoped>
.corner {
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.login-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding-top: 15vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.v-card {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.9) !important;
}
</style>