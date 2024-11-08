import request from './request'

export const getTasks = () => {
    return request({
        url: '/pro/project_detail',
        method: 'get'
    })
}

export const addTask = (data) => {
    return request({
        url: '/pro/project_detail',
        method: 'post',
        data
    })
}

