import axios from 'axios'

// 创建axios实例
const request = axios.create({
    baseURL: process.env.VUE_APP_BASE_API, // 从环境变量获取基础URL
    timeout: 5000  // 请求超时时间
})

// 请求拦截器
request.interceptors.request.use(
    config => {
        // 从localStorage或vuex获取token
        const token = localStorage.getItem('token')
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`
        }
        return config
    },
    error => {
        console.error('请求错误：', error)
        return Promise.reject(error)
    }
)

// 响应拦截器
request.interceptors.response.use(
    response => {
        const res = response.data
        // 这里可以根据后端的响应结构做统一的处理
        return res
    },
    error => {
        console.error('响应错误：', error)
        // 这里可以统一处理错误，比如401、500等状态码
        return Promise.reject(error)
    }
)

export default request