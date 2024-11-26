import axios from 'axios'


const request = axios.create({
    baseURL: process.env.VUE_APP_BASE_API, 
    timeout: 5000  
})


request.interceptors.request.use(
    config => {
        const token = sessionStorage.getItem('token')
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

export default request