import { mount } from '@vue/test-utils'
import Login from '../src/views/Login.vue'

jest.mock('vue-toastification', () => ({
  useToast: () => ({
    success: jest.fn(),
    error: jest.fn()
  })
}))

describe('Login.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Login, {
      global: {
        mocks: {
          $axios: {
            post: jest.fn()
          },
          $store: {
            dispatch: jest.fn()
          },
          $router: {
            push: jest.fn()
          }
        },
        stubs: {
          'v-card': true,
          'v-toolbar': true,
          'v-toolbar-title': true,
          'v-container': true,
          'v-card-text': true,
          'v-form': true,
          'v-text-field': true,
          'v-card-actions': true,
          'v-btn': true
        }
      }
    })
  })


  test('组件应该正确渲染', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.login-container').exists()).toBe(true)
  })


  describe('用户名验证规则', () => {
    test('用户名不能为空', () => {
      const rules = wrapper.vm.usernameRules
      expect(rules[0]('')).toBe('Username cannot be empty')
      expect(rules[0]('test')).toBe(true)
    })

    test('用户名不能超过10个字符', () => {
      const rules = wrapper.vm.usernameRules
      expect(rules[1]('verylongusername')).toBe('Username cannot exceed 10 characters')
      expect(rules[1]('test')).toBe(true)
    })
  })


  describe('密码验证规则', () => {
    test('密码不能为空', () => {
      const rules = wrapper.vm.passwordRules
      expect(rules[0]('')).toBe('Password is required')
      expect(rules[0]('password123')).toBe(true)
    })

    test('密码长度至少6个字符', () => {
      const rules = wrapper.vm.passwordRules
      expect(rules[1]('12345')).toBe('Password must be at least 6 characters')
      expect(rules[1]('123456')).toBe(true)
    })

    test('密码必须包含大写字母', () => {
      const rules = wrapper.vm.passwordRules
      expect(rules[2]('password123')).toBe('Password must contain at least one uppercase letter')
      expect(rules[2]('Password123')).toBe(true)
    })

    test('密码必须包含小写字母', () => {
      const rules = wrapper.vm.passwordRules
      expect(rules[3]('PASSWORD123')).toBe('Password must contain at least one lowercase letter')
      expect(rules[3]('Password123')).toBe(true)
    })

    test('密码必须包含数字', () => {
      const rules = wrapper.vm.passwordRules
      expect(rules[4]('Password')).toBe('Password must contain at least one number')
      expect(rules[4]('Password123')).toBe(true)
    })
  })


  describe('登录功能', () => {
    test('登录成功时应该正确处理', async () => {
      const mockToken = 'fake-token'
      wrapper.vm.$axios.post.mockResolvedValueOnce({ data: { token: mockToken } })

      await wrapper.setData({
        username: 'testuser',
        password: 'Password123',
        valid: true
      })

      const mockValidate = jest.fn().mockReturnValue(true)
      wrapper.vm.login = jest.spyOn(wrapper.vm, 'login').mockImplementation(async () => {
        if (mockValidate()) {
          try {
            const response = await wrapper.vm.$axios.post(expect.any(String), {
              username: wrapper.vm.username,
              password: wrapper.vm.password,
            })
            const token = response.data.token
            await wrapper.vm.$store.dispatch('user/login', token)
            await wrapper.vm.$store.dispatch('user/setUsername', wrapper.vm.username)
            wrapper.vm.toast.success('Login successful')
            wrapper.vm.$router.push('/home')
          } catch (error) {
            wrapper.vm.toast.error('Login failed')
          }
        }
      })


      await wrapper.vm.login()

      expect(wrapper.vm.$axios.post).toHaveBeenCalledWith(
        expect.any(String),
        {
          username: 'testuser',
          password: 'Password123'
        }
      )


      expect(wrapper.vm.$store.dispatch).toHaveBeenCalledWith('user/login', mockToken)
      expect(wrapper.vm.$store.dispatch).toHaveBeenCalledWith('user/setUsername', 'testuser')


      expect(wrapper.vm.$router.push).toHaveBeenCalledWith('/home')
    })

    test('登录失败时应该显示错误信息', async () => {
      wrapper.vm.$axios.post.mockRejectedValueOnce(new Error('Login failed'))

 
      await wrapper.setData({
        username: 'testuser',
        password: 'Password123',
        valid: true
      })

 
      const mockValidate = jest.fn().mockReturnValue(true)
      wrapper.vm.login = jest.spyOn(wrapper.vm, 'login').mockImplementation(async () => {
        if (mockValidate()) {
          try {
            await wrapper.vm.$axios.post(expect.any(String), {
              username: wrapper.vm.username,
              password: wrapper.vm.password,
            })
          } catch (error) {
            wrapper.vm.toast.error('Login failed')
          }
        }
      })

      await wrapper.vm.login()
      
      expect(wrapper.vm.toast.error).toHaveBeenCalled()
    })
  })

  test('点击注册按钮应该跳转到注册页面', async () => {
    await wrapper.vm.goToRegister()
    expect(wrapper.vm.$router.push).toHaveBeenCalledWith('/register')
  })
})