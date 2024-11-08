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

export const getProjectMembers = (params) => {
    return request({
        url: `/pro/edit_project_member`,
        method: 'get',
        params
    })
}

export const manageProjectMember = (data) => {
    return request({
        url: `/pro/edit_project_member`,
        method: 'post',
        data,
    })
}
