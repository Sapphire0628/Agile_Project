import request from './request'

export const getProjects = () => {
    return request({
        url: '/pro/project',
        method: 'get',
    })
}

export const addProject = (data) => {
    return request({
        url: '/pro/project',
        method: 'post',
        data,
    })
}

export const deleteProject = (data) => {  
    return request({
        url: `/pro/project`,
        method: 'delete',
        data
    })
}

export const updateProject = (data) => {
    return request({
        url: `/pro/project`,
        method: 'put',
        data,
    })
}
