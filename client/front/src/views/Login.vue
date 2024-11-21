<template>
  <div class="login-container">
    <v-card class="corner" width="500px">
      <v-toolbar color="primary">
        <v-toolbar-title>登录</v-toolbar-title>
      </v-toolbar>
      <v-container fluid>
        <v-card-text>
          <v-form @keyup.enter.native="login" v-model="valid" ref="form" lazy-validation>
            <v-text-field
            v-model="username"
            label="用户名"
            :rules="usernameRules"
            :counter="10"
            required
            prepend-inner-icon="mdi mdi-account"
          ></v-text-field>
            <v-text-field
              v-model="password"
              :rules="passwordRules"
              label="密码"
              required
              prepend-inner-icon="mdi mdi-lock"
            ></v-text-field>
          </v-form>
            <v-card-actions class="d-flex justify-center">
              <v-btn variant="outlined" color="primary" :disabled="!valid" @click="login">登录</v-btn>
              <v-btn variant="outlined" @click="goToRegister">没有账号？注册</v-btn>
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
      v => !!v || '用户名不能为空',
      v => (v&&v.length <= 10) || '用户名不能超过10个字符'
      ],
      password: '',
      passwordRules: [
      v => !!v || '密码是必填项',
        v => v.length >= 6 || '密码必须至少6个字符',
        v => /[A-Z]/.test(v) || '密码必须包含至少一个大写字母',
        v => /[a-z]/.test(v) || '密码必须包含至少一个小写字母',
        v => /[0-9]/.test(v) || '密码必须包含至少一个数字'
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
            this.toast.success('登录成功')
            this.$router.push('/home')
            console.log('登录成功')
          })
          .catch(() => {
            this.toast.error('登录失败')
            console.log('登陆失败')
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