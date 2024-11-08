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

