from flask import Blueprint, request, jsonify
import os
import sqlite3

pro_bp = Blueprint('pro', __name__)


def get_db_connection():
    try:
        DB_PATH = os.path.abspath(os.path.join(os.getcwd(), 'database', 'test.db'))
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise


def get_user_project(user_id):
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
                   SELECT DISTINCT p. project_id, p.project_name, p.description,p.owner_id, p.created_at
                   FROM UserTask ut, ProjectTask pt, Projects p
                   WHERE ut.task_id = pt.task_id and ut.user_id = ? AND pt.project_id = p.project_id
               ''', (user_id,))
        projects = cursor.fetchall()
        return projects
    except Exception as e:
        print(str(e))
    finally:
        conn.close()


def get_own_project(user_id):
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
                   SELECT p. project_id, p.project_name, p.description,p.owner_id, p.created_at
                   FROM  Projects p
                   WHERE owner_id = ?
               ''', (user_id,))
        all_project = cursor.fetchall()
        return all_project
    except Exception as e:
        print(str(e))
    finally:
        conn.close()


def get_user_tasks(user_id):
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
                       SELECT t.task_id, t.task_name, t.description, t.status, t.priority, t.due_date, t.created_at
                       FROM UserTask ut, Tasks t
                       WHERE ut.user_id = ? AND ut.task_id = t.task_id
                   ''', (user_id,))
        all_task = cursor.fetchall()
        return all_task
    finally:
        conn.close()


def get_project_detail(data):
    required_fields = ['project_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    project_id = data['project_id']

    conn = get_db_connection()
    try:
        # get project detail
        cursor = conn.execute('SELECT * FROM Projects WHERE project_id = ?', (project_id,))
        pro = cursor.fetchone()

        if pro:
            pro_dict = {
                'pro_id': pro[0],
                'name': pro[1],
                'description': pro[2],
                'owner_id': pro[3],
                'created_at': pro[4]
            }
            cursor = conn.execute(
                'SELECT DISTINCT username FROM Users u,UserTask ut, ProjectTask pt WHERE u.user_id = ut.user_id and ut.task_id = pt.task_id and pt.project_id = ?',
                (project_id,))
            members = cursor.fetchall()

            cursor = conn.execute(
                'SELECT t.task_id, task_name, description, status, priority, due_date, created_at  FROM Tasks t,ProjectTask pt WHERE t.task_id = pt.task_id and pt.project_id = ?',
                (project_id,))
            tasks = cursor.fetchall()

            return jsonify({
                'message': 'open project successfully',
                'project_id': project_id,
                'name': pro_dict['name'],
                'description': pro_dict['description'],
                'owner_id': pro_dict['owner_id'],
                'created_at': pro_dict['created_at'],
                'Members': members,
                'tasks': tasks
            }), 200
        else:
            return jsonify({'error': 'Invalid Project id'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


def register_task(data):
    # Validate required fields, description is option
    #  task_id and created_at are created by server
    required_fields = ['task_name', 'status', 'priority', 'due_date', 'users']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    try:
        cursor = conn.execute('SELECT owner_id FROM Projects WHERE project_id = ?',
                              (data['project_id'],))
        owner_id = cursor.fetchone()
        if owner_id is None:
            return jsonify({'error': 'No such project'}), 400
        else:
            owner_id = owner_id[0]

        if owner_id != data['creator_id']:
            return jsonify({'error': 'Owner ID mismatch'}), 400

        user_id = []
        # through user_name get user_id
        for user in data['users']:
            cursor = conn.execute('SELECT user_id FROM Users WHERE username = ?',
                                  (user,))
            user_id.append(cursor.fetchone()[0])

        if 'description' not in data.keys():
            des = ""
        else:
            des = data['description']
        # event_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Create new Task
        cursor = conn.execute('''
                INSERT INTO Tasks (task_name, description, status, priority, due_date)
                VALUES (?, ?, ?,?,?)
            ''', (data['task_name'], des, data['status'], data['priority'], data['due_date']))
        conn.commit()
        index = cursor.lastrowid

        # Create new Project_Task
        conn.execute('''
                INSERT INTO ProjectTask (project_id, task_id)
                VALUES (?, ?)
            ''', (data['project_id'], index))
        conn.commit()

        # Create new UserTask
        for user in user_id:
            conn.execute('''
                            INSERT INTO UserTask (user_id, task_id)
                            VALUES (?, ?)''',
                         (user, index))
        conn.commit()
        return jsonify({'message': 'Task registered successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


def register_project(data):
    # Validate required fields, description is optional
    # project_id, owner_id and created_at are created by server
    required_fields = ['project_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    try:
        if 'description' not in data.keys():
            des = ""
        else:
            des = data['description']

        # event_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if 'project_id' in data.keys():
            conn.execute('''
                            INSERT INTO Projects (project_id, project_name, description, owner_id)
                            VALUES (?, ?, ?,?)''',
                         (data['project_id'], data['project_name'], des, data['owner_id']))
            conn.commit()
        # Create new Project
        else:
            conn.execute('''
                INSERT INTO Projects (project_name, description, owner_id)
                VALUES (?, ?,?)''',
                         (data['project_name'], des, data['owner_id']))
        conn.commit()

        return jsonify({'message': 'Project registered successfully'}), 201
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


def delete_project(data):
    required_fields = ['project_id', 'creator_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    project_id = data['project_id']
    conn = get_db_connection()
    try:
        cursor = conn.execute('SELECT owner_id FROM Projects WHERE project_id = ?',
                              (data['project_id'],))
        owner_id = cursor.fetchone()
        if owner_id is None:
            return jsonify({'error': 'No such project'}), 400
        else:
            owner_id = owner_id[0]

        if owner_id != data['creator_id']:
            return jsonify({'error': 'Owner ID mismatch'}), 400

        conn.execute('''DELETE FROM Projects WHERE project_id = ?''',
                     (project_id,))
        cursor = conn.execute('''SELECT task_id FROM ProjectTask WHERE ProjectTask.project_id = ?''', (project_id,))
        task_ids = cursor.fetchall()
        for task_id in task_ids:
            id = task_id[0]
            conn.execute('''DELETE FROM Tasks WHERE  task_id = ?''',
                         (id,))
            conn.execute('''DELETE FROM ProjectTask WHERE task_id = ?''',
                         (id,))
            conn.execute('''DELETE FROM UserTask WHERE task_id = ?''',
                         (id,))
        conn.commit()
        return jsonify({'message': 'Project deleted successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


def delete_task(data):
    required_fields = ['task_id', 'creator_id', 'owner_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    task_id = data['task_id']
    conn = get_db_connection()
    try:
        cursor = conn.execute('SELECT * FROM Tasks WHERE task_id = ?',
                              (task_id,))
        task = cursor.fetchone()
        if task is None:
            return jsonify({'error': 'No such task'}), 400

        if data['owner_id'] != data['creator_id']:
            return jsonify({'error': 'Owner ID mismatch'}), 400

        conn.execute('''DELETE FROM Tasks WHERE  task_id = ?''',
                     (task_id,))
        conn.execute('''DELETE FROM ProjectTask WHERE task_id = ?''',
                     (task_id,))
        conn.execute('''DELETE FROM UserTask WHERE task_id = ?''',
                     (task_id,))
        conn.commit()

        return jsonify({'message': 'Task deleted successfully'}), 201
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


def update_task(data):
    required_fields = ['task_id', 'creator_id', 'owner_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    conn = get_db_connection()
    task_id = data['task_id']
    try:
        cursor = conn.execute('''SELECT * FROM Tasks WHERE task_id = ?''',
                              (task_id,))
        task = cursor.fetchone()
        if task is None:
            return jsonify({'error': 'No such task'}), 400

        if data['owner_id'] != data['creator_id']:
            return jsonify({'error': 'Owner ID mismatch'}), 400

        if 'task_name' in data.keys():
            conn.execute('''UPDATE Tasks
                            SET task_name = ?
                            WHERE Tasks.task_id = ?''',
                         (data['task_name'], task_id,))
        if 'description' in data.keys():
            conn.execute('''UPDATE Tasks
                            SET description = ?
                            WHERE Tasks.task_id = ?''',
                         (data['description'], task_id,))
        if 'status' in data.keys():
            conn.execute('''UPDATE Tasks
                            SET status = ?
                            WHERE Tasks.task_id = ?''',
                         (data['status'], task_id,))
        if 'priority' in data.keys():
            conn.execute('''UPDATE Tasks
                            SET priority = ?
                            WHERE Tasks.task_id = ?''',
                         (data['priority'], task_id,))
        if 'due_date' in data.keys():
            conn.execute('''UPDATE Tasks
                            SET due_date = ?
                            WHERE Tasks.task_id = ?''',
                         (data['due_date'], task_id,))
        if 'user' in data.keys():
            cursor = conn.execute('''SELECT user_id FROM UserTask WHERE task_id = ?''',
                                  (task_id,))
            id = cursor.fetchall()
            ids = []
            for item in id:
                ids.append(item[0])

            if data['user']['type'] == 'add':
                common_elements = set(ids) & set(data['user']['users'])
                if common_elements:
                    return jsonify({'err': 'user already exits.', 'users:': list(common_elements)}), 400

                for user_id in data['user']['users']:
                    conn.execute('''INSERT INTO UserTask (user_id, task_id)
                                VALUES (?, ?)''',
                                 (user_id, task_id,))

            elif data['user']['type'] == 'remove':
                different_elements = set(data['user']['users']).difference(set(ids))
                if different_elements:
                    return jsonify({'err': 'user not exits.','users:':list(different_elements)}), 400
                for user_id in data['user']['users']:
                    conn.execute('''DELETE FROM UserTask WHERE  user_id = ? and task_id = ?''',
                                 (user_id, task_id,))
            else:
                return jsonify({'err': 'No such update task opration'}), 400

        conn.commit()
        return jsonify({'message': 'Task updated successfully'}), 201
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


def update_project(data):
    required_fields = ['project_id', 'creator_id', 'owner_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    conn = get_db_connection()
    project_id = data['project_id']
    try:
        cursor = conn.execute('''SELECT * FROM Projects WHERE project_id = ?''',
                              (project_id,))
        project = cursor.fetchone()
        if project is None:
            return jsonify({'error': 'No such Project'}), 400

        if data['owner_id'] != data['creator_id']:
            return jsonify({'error': 'Owner ID mismatch'}), 400

        if 'project_name' in data.keys():
            conn.execute('''UPDATE Projects
                                SET project_name = ?
                                WHERE Projects.project_id = ?''',
                         (data['project_name'], project_id,))
        if 'description' in data.keys():
            conn.execute('''UPDATE Projects
                                SET description = ?
                                WHERE Projects.project_id = ?''',
                         (data['description'], project_id,))
        if 'replace_owner_id' in data.keys():
            conn.execute('''UPDATE Projects
                                SET owner_id = ?
                                WHERE Projects.project_id = ?''',
                         (data['owner_id'], project_id,))
        conn.commit()
        return jsonify({'message': 'Project updated successfully'}), 201
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# This page show all task of one task and can register task
@pro_bp.route('/project_detail', methods=['POST', 'GET', 'DELETE', 'PUT'])
def project_detail():
    # 用户注册、更新任务
    data = request.get_json()
    if request.method == "GET":
        return get_project_detail(data)

    elif request.method == "POST":
        return register_task(data)

    elif request.method == "DELETE":
        return delete_task(data)

    elif request.method == "PUT":
        return update_task(data)


# This page show all project and tasks of one user and can register project
@pro_bp.route('/project', methods=['POST', 'GET', 'DELETE', 'PUT'])
def project():
    # 用户注册、更新项目
    data = request.get_json()
    print(request.method)
    if request.method == "GET":
        all_project = get_user_project(data['user_id'])
        all_own_project = get_own_project(data['user_id'])
        all_tasks = get_user_tasks(data['user_id'])

        return jsonify({'message': 'show all project successfully',
                        'project_belong': all_project,
                        'own_project': all_own_project,
                        'tasks': all_tasks}), 201

    elif request.method == "POST":
        return register_project(data)

    elif request.method == "DELETE":
        return delete_project(data)

    elif request.method == "PUT":
        return update_project(data)
