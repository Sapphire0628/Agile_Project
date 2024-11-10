<template>
    <v-card class="corner" width="500px">
        <v-toolbar>
          <v-toolbar-title class="text-center w-100">注册</v-toolbar-title>
        </v-toolbar>
        <v-container fluid>
          <v-card-text>
            <v-form @keyup.enter.native="register" v-model="valid" ref="form" lazy-validation>
              <v-text-field
                v-model="username"
                label="用户名"
                :rules="usernameRules"
                :counter="10"
                required
                prepend-inner-icon="mdi-account"
              ></v-text-field>
              <v-text-field
                v-model="email"
                :rules="emailRules"
                label="电子邮件"
                required
                prepend-inner-icon="mdi-email"
              ></v-text-field>
              <v-text-field
                v-model="password"
                :rules="passwordRules"
                label="密码"
                required
                prepend-inner-icon="mdi-lock"
              ></v-text-field>
            </v-form>
              <v-card-actions class="d-flex justify-center">
                <v-btn variant="outlined" color="primary" :disabled="!valid" @click="register">注册</v-btn>
                <v-btn variant="outlined" @click="getback">返回</v-btn>
              </v-card-actions>
          </v-card-text>
        </v-container>
      </v-card>
</template>

<script>
export default {
data:() => ({
    valid: true,
    username: '',
    usernameRules: [
      v => !!v || '用户名不能为空',
      v => (v&&v.length <= 10) || '用户名不能超过10个字符'
    ],
    email: '',
    emailRules: [
      v => !!v || '电子邮件不能为空',
      v => /.+@.+\..+/.test(v) || '电子邮件格式不正确'
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
  register() {
    if (this.$refs.form.validate()) {
        this.$axios.post('https://b06d2e0d-a156-474f-adfa-a53fade93306-00-392iabnynab1k.pike.replit.dev/auth/register', {
          username: this.username,
          email: this.email,
          password: this.password,
        })
        .then(() => {
          console.log('注册成功')
          this.$router.push('/login')
        })
        .catch(() =>{
          console.log('注册失败')
        })
      }
  },
  clear() {
      this.$refs.form.reset();
    },
  getback() {
    this.$router.push('/login');
  },
}
}
</script>

<style scope>
.corner{
border-radius: 15px;
}

</style>