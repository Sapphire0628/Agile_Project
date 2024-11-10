import request from './request'

export const getSprints = (params) => {
    return request({
        url: '/pro/sprint',
        method: 'get',
        params
    })
}

export const createSprint = (data) => {
    return request({
        url: '/pro/sprint',
        method: 'post',
        data
    })
}

export const updateSprintTask = (data) => {
    return request({
        url: '/pro/edit_sprint_task',
        method: 'post',
        data
    })
}
