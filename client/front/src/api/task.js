import request from './request'

export const getTasks = (params) => {
    return request({
        url: `/pro/project_detail`,
        method: 'get',
        params
    })
}

export const addTask = (data) => {
    return request({
        url: '/pro/project_detail',
        method: 'post',
        data
    })
}

export const updateTask = (data) => {
    return request({
        url: '/pro/project_detail',
        method: 'put',
        data
    })
}

export const deleteTask = (data) => {
    return request({
        url: '/pro/project_detail',
        method: 'delete',
        data
    })
}


