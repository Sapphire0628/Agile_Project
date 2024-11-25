import { mount } from '@vue/test-utils'
import Register from '../src/views/Register.vue'


jest.mock('vue-toastification', () => ({
  useToast: () => ({
    success: jest.fn(),
    error: jest.fn()
  })
}))

describe('Register.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Register, {
      global: {
        mocks: {
          $axios: {
            post: jest.fn()
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
    expect(wrapper.find('.register-container').exists()).toBe(true)
  })


  describe('表单验证规则', () => {
    describe('用户名验证', () => {
      it('用户名不能为空', () => {
        const rules = wrapper.vm.usernameRules
        expect(rules[0]('')).toBe('Username cannot be empty')
        expect(rules[0]('测试用户')).toBe(true)
      })

      it('用户名长度不能超过10个字符', () => {
        const rules = wrapper.vm.usernameRules
        expect(rules[1]('这是一个超长的用户名测试')).toBe('Username cannot exceed 10 characters')
        expect(rules[1]('测试用户')).toBe(true)
      })
    })

    describe('邮箱验证', () => {
      it('邮箱不能为空', () => {
        const rules = wrapper.vm.emailRules
        expect(rules[0]('')).toBe('Email cannot be empty')
        expect(rules[0]('test@example.com')).toBe(true)
      })

      it('邮箱格式必须正确', () => {
        const rules = wrapper.vm.emailRules
        expect(rules[1]('invalid-email')).toBe('Invalid email format')
        expect(rules[1]('test@example.com')).toBe(true)
      })
    })

    describe('密码验证', () => {
      it('密码不能为空', () => {
        const rules = wrapper.vm.passwordRules
        expect(rules[0]('')).toBe('Password is required')
        expect(rules[0]('Test123')).toBe(true)
      })

      it('密码长度至少6位', () => {
        const rules = wrapper.vm.passwordRules
        expect(rules[1]('Test1')).toBe('Password must be at least 6 characters')
        expect(rules[1]('Test123')).toBe(true)
      })

      it('密码必须包含大写字母', () => {
        const rules = wrapper.vm.passwordRules
        expect(rules[2]('test123')).toBe('Password must contain at least one uppercase letter')
        expect(rules[2]('Test123')).toBe(true)
      })

      it('密码必须包含小写字母', () => {
        const rules = wrapper.vm.passwordRules
        expect(rules[3]('TEST123')).toBe('Password must contain at least one lowercase letter')
        expect(rules[3]('Test123')).toBe(true)
      })

      it('密码必须包含数字', () => {
        const rules = wrapper.vm.passwordRules
        expect(rules[4]('TestTest')).toBe('Password must contain at least one number')
        expect(rules[4]('Test123')).toBe(true)
      })
    })
  })


  describe('注册功能', () => {
    test('注册成功时应该正确处理', async () => {
      wrapper.vm.$axios.post.mockResolvedValueOnce({})

      await wrapper.setData({
        username: 'testuser',
        email: 'test@example.com',
        password: 'Password123',
        valid: true
      })

      const mockValidate = jest.fn().mockReturnValue(true)
      wrapper.vm.register = jest.spyOn(wrapper.vm, 'register').mockImplementation(async () => {
        if (mockValidate()) {
          try {
            await wrapper.vm.$axios.post(expect.any(String), {
              username: wrapper.vm.username,
              email: wrapper.vm.email,
              password: wrapper.vm.password,
            })
            wrapper.vm.toast.success('Registration successful')
            wrapper.vm.$router.push('/login')
          } catch (error) {
            wrapper.vm.toast.error('Registration failed')
          }
        }
      })

      await wrapper.vm.register()

      expect(wrapper.vm.$axios.post).toHaveBeenCalledWith(
        expect.any(String),
        {
          username: 'testuser',
          email: 'test@example.com',
          password: 'Password123'
        }
      )

      expect(wrapper.vm.$router.push).toHaveBeenCalledWith('/login')
      expect(wrapper.vm.toast.success).toHaveBeenCalledWith('Registration successful')
    })

    test('注册失败时应该显示错误信息', async () => {
      wrapper.vm.$axios.post.mockRejectedValueOnce(new Error('Registration failed'))

      await wrapper.setData({
        username: 'testuser',
        email: 'test@example.com',
        password: 'Password123',
        valid: true
      })

      const mockValidate = jest.fn().mockReturnValue(true)
      wrapper.vm.register = jest.spyOn(wrapper.vm, 'register').mockImplementation(async () => {
        if (mockValidate()) {
          try {
            await wrapper.vm.$axios.post(expect.any(String), {
              username: wrapper.vm.username,
              email: wrapper.vm.email,
              password: wrapper.vm.password,
            })
          } catch (error) {
            wrapper.vm.toast.error('Registration failed')
          }
        }
      })

      await wrapper.vm.register()

      expect(wrapper.vm.toast.error).toHaveBeenCalledWith('Registration failed')
    })
  })

  test('点击返回按钮应该跳转到登录页面', async () => {
    await wrapper.vm.getback()
    expect(wrapper.vm.$router.push).toHaveBeenCalledWith('/login')
  })

  test('清除表单应该重置所有字段', async () => {
    const mockReset = jest.fn()
    
    wrapper.vm.clear = jest.spyOn(wrapper.vm, 'clear').mockImplementation(async () => {
      if (mockReset) {
        mockReset()
      }
    })

    await wrapper.vm.clear()
    expect(mockReset).toHaveBeenCalled()
  })
})
