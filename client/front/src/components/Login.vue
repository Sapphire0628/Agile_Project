<template>
      <v-card class="corner" width="500px">
          <v-toolbar>
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
                prepend-inner-icon="fa fa-user"
              ></v-text-field>
                <v-text-field
                  v-model="password"
                  :rules="passwordRules"
                  label="密码"
                  required
                  prepend-inner-icon="fa fa-lock"
                ></v-text-field>
              </v-form>
                <v-card-actions class="d-flex justify-center">
                  <v-btn variant="outlined" color="primary" :disabled="!valid" @click="login">登录</v-btn>
                  <v-btn variant="outlined" @click="goToRegister">没有账号？注册</v-btn>
                </v-card-actions>
            </v-card-text>
          </v-container>
        </v-card>
</template>

<script>
import axios from 'axios';

export default {
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
          axios.post('/https://8a74705f-88cc-40ba-af38-3379f495a983-00-1npdqf5pljqau.pike.replit.dev/auth/login/', {
            username: this.username,
            password: this.password,
          })
          .then(() => {
            console.log('登录成功')
          })
          .catch(() =>{
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

<style scope>
.corner{
  border-radius: 15px;
}

</style>