import request from './request'

export const getTaskComments = (taskId) => {
  return request({
    url: '/pro/comment',
    method: 'get',
    params: { task_id: taskId }
  })
}

export const addComment = (data) => {
    return request({
        url: '/pro/comment',
        method: 'post',
        data,
    })
}

export const deleteComment = (data) => {
    return request({
        url: '/pro/comment',
        method: 'delete',
        data,
    })
}

export const updateComment = (data) => {
    return request({
        url: '/pro/comment',
        method: 'put',
        data,
    })
}
