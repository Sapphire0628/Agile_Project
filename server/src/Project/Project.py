from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import jwt
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

def get_owner_id(project_id):
    conn = get_db_connection()
    cursor = conn.execute('SELECT owner_id FROM Projects WHERE project_id = ?',
                          (project_id,))
    owner_id = cursor.fetchone()
    conn.close()
    if owner_id is None:
        return -1
    else:
        owner_id = owner_id[0]
        return owner_id

def ids_to_names(ids):
    conn = get_db_connection()
    cursor = conn.cursor()
    users = []
    for id in ids:
        cursor.execute('''SELECT username FROM Users WHERE user_id = ?''',
                       (id,))
        id = cursor.fetchone()
        if id:
            users.append(id[0])
    conn.close()
    return users

def get_sprint(args):
    project_id = args['project_id']

    conn = get_db_connection()
    try:
        # get sprint detail
        cursor = conn.execute('SELECT * FROM Projects WHERE project_id = ?', (project_id,))
        pro = cursor.fetchone()

        if pro:
            cursor = conn.cursor()
            cursor.execute(''' SELECT round, task_id, start_at, due_date, name FROM  Sprint WHERE  project_id = ?
                                       ''', (project_id,))
            sprints = cursor.fetchall()
            print(str(sprints))
            test = {}
            for sprint in sprints:
                round = sprint[0]
                task_id = sprint[1]
                start_at = sprint[2]
                due_date = sprint[3]
                name = sprint[4]
                if round not in test.keys():
                    test[round] = {}
                test[round]['round'] = round
                test[round]['start_at'] = start_at
                test[round]['due_date'] = due_date
                test[round]['name'] = name

                if 'tasks' not in test[round].keys():
                    test[round]['total_tasks'] = []
                    test[round]['completed_task'] = []

                if task_id is None:
                    continue
                cursor = conn.execute(
                    '''SELECT task_name, status FROM Tasks WHERE task_id = ?''', (task_id,))
                task = cursor.fetchone()
                taskname = task[0]
                status = task[1]
                test[round]['total_tasks'].append({'name':taskname,
                                                   'id':task_id})
                if status == 'Done':
                    test[round]['completed_task'].append({'name':taskname,
                                                   'id':task_id})

            return jsonify(test), 200
        else:
            return jsonify({'error': 'Invalid Project id'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

def get_user_project(user_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
                           SELECT DISTINCT p.project_id, p.project_name, p.description,p.owner_id, p.created_at
                           FROM UserProject up, Projects p
                           WHERE up.user_id = ? AND up.project_id = p.project_id
                       ''', (user_id,))
        projects = cursor.fetchall()
        projects = [{'project_id': p[0], 'project_name': p[1], 'description': p[2], 'owner_id': p[3], 'created_at': p[4]} for p in projects]
        return projects
    except Exception as e:
        print(str(e))
    finally:
        conn.close()


def get_own_project(user_id):
    conn = get_db_connection()
    try:
        
        cursor = conn.cursor()
        cursor.execute('''
                   SELECT p. project_id, p.project_name, p.description,p.owner_id, p.created_at
                   FROM  Projects p
                   WHERE owner_id = ?
               ''', (user_id,))
        all_project = cursor.fetchall()

        all_project = [{'project_id': p[0], 'project_name': p[1], 'description': p[2], 'owner_id': p[3], 'created_at': p[4]} for p in all_project]
        return all_project
    except Exception as e:
        print(str(e))
    finally:
        conn.close()


def get_user_tasks(user_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT t.task_id, t.task_name, t.description, t.status, t.priority, t.due_date, t.created_at
                       FROM UserTask ut, Tasks t
                       WHERE ut.user_id = ? AND ut.task_id = t.task_id
                   ''', (user_id,))
        all_task = cursor.fetchall()
        all_task = [{'task_id': t[0], 'task_name': t[1], 'description': t[2], 'status': t[3], 'priority': t[4], 'due_date': t[5], 'created_at': t[6]} for t in all_task]

        return all_task
    finally:
        conn.close()


def get_project_detail(data):
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
            cursor = conn.cursor()
            cursor.execute(''' SELECT username FROM  Users WHERE  user_id = ?
                                   ''', (pro_dict['owner_id'],))
            owner = cursor.fetchone()[0]

            cursor = conn.execute(
                'SELECT DISTINCT username FROM Users u, UserProject up WHERE u.user_id = up.user_id and up.project_id = ?',
                (project_id,))
            members = cursor.fetchall()
            members = [{'username': m[0]} for m in members]

            cursor = conn.execute(
                '''SELECT t.task_id, t.task_name, t.description, t.status, t.priority, t.due_date, t.created_at
                   FROM Tasks t, ProjectTask pt
                   WHERE t.task_id = pt.task_id and pt.project_id = ?
                   and t.task_id not in (select distinct task_id from Sprint where project_id = ? and task_id is not null)''',
                (project_id,project_id,))
            tasks = cursor.fetchall()
            tasks = [{'task_id': t[0], 'task_name': t[1], 'description': t[2], 'status': t[3], 'priority': t[4], 'due_date': t[5], 'created_at': t[6]} for t in tasks]

            return jsonify({
                'message': 'open project successfully',
                'project_id': project_id,
                'name': pro_dict['name'],
                'description': pro_dict['description'],
                'owner_id': pro_dict['owner_id'],
                'owner_name': owner,
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
    required_fields = ['task_name', 'project_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    if 'status' not in data.keys():
        data['status'] = 'Not start'

    if 'priority' not in data.keys():
        data['priority'] = '0'

    if 'description' not in data.keys():
        data['description'] = ""

    conn = get_db_connection()
    try:
        owner_id = get_owner_id(data['project_id'])
        if owner_id == -1:
            return jsonify({'error': 'No such project'}), 400

        if owner_id != data['creator_id']:
            return jsonify({'error': 'Owner ID mismatch'}), 400


        if not 'due_date' in data.keys():
            cursor = conn.execute('''
                            INSERT INTO Tasks (task_name, description, status, priority)
                            VALUES (?, ?, ?,?)
                        ''', (data['task_name'], data['description'], data['status'], data['priority']))
            conn.commit()
        else:
            cursor = conn.execute('''
                            INSERT INTO Tasks (task_name, description, status, priority,due_date)
                            VALUES (?, ?, ?,?,?)
                        ''', (data['task_name'], data['description'], data['status'], data['priority'], data['due_date']))
            conn.commit()

        index = cursor.lastrowid

        # Create new Project_Task
        conn.execute('''
                        INSERT INTO ProjectTask (project_id, task_id)
                        VALUES (?, ?)
                    ''', (data['project_id'], index))
        conn.commit()

        if 'users' in data.keys():
            user_id = []
            invalid_name = []
            # through user_name get user_id
            for user in data['users']:
                cursor = conn.execute('SELECT user_id FROM Users WHERE username = ?',
                                      (user,))
                i = cursor.fetchone()
                if i is None:
                    invalid_name.append(user)
                else:
                    user_id.append(i[0])

            if len(invalid_name) != 0:
                return jsonify({'err': 'Invalid user.', 'users:': invalid_name}), 400


            cursor = conn.execute('SELECT user_id FROM UserProject WHERE project_id = ?',
                                  (data['project_id'],))
            ids = cursor.fetchall()
            valid_id = []
            for id in ids:
                valid_id.append(id[0])
            project_owner = get_owner_id(project_id=data['project_id'])
            valid_id.append(project_owner)

            if not set(user_id).issubset(valid_id):
                return jsonify({'error': 'Invalid User ID'}), 400

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
                         (data['project_id'], data['project_name'], des, data['creator_id']))
            conn.commit()
        # Create new Project
        else:
            conn.execute('''
                INSERT INTO Projects (project_name, description, owner_id)
                VALUES (?, ?,?)''',
                         (data['project_name'], des, data['creator_id']))
        conn.commit()

        response = jsonify({'message': 'Project registered successfully',
                        'owner_id': data['creator_id'],
                        'project_name':data['project_name']})
        # response.headers['Authorization'] = f'Bearer {access_token}'

        return response, 200 
    
    except Exception as e:
        print(str(e))
        return jsonify({'Error': str(e)}), 500
    finally:
        conn.close()

def register_sprint(data):
    # Validate required fields, description is optional
    required_fields = ['name','project_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    owner_id = get_owner_id(data['project_id'])
    if owner_id == -1:
        return jsonify({'error': 'No such project'}), 400

    if owner_id != data['creator_id']:
        return jsonify({'error': 'Owner ID mismatch'}), 400
    conn = get_db_connection()

    try:
        if 'round' not in data.keys():
            data['round'] = 0
        if 'due_date' not in data.keys():
            data['due_date'] = None
        # if 'start_at' not in data.keys():
        #     data['start_at'] = None

        if 'tasks' not in data.keys():
            conn.execute('''
            INSERT INTO Sprint (round, name, project_id, due_date) values (?,?,?,?)''',
                         (data['round'],data['name'],data['project_id'], data['due_date']))
            conn.commit()
            return jsonify({'message': 'Sprint registered successfully'}), 200
        else:
            cursor = conn.cursor()
            cursor.execute('''
                               SELECT task_id
                               FROM  ProjectTask
                               WHERE project_id = ?
                           ''', (data['project_id'],))
            valid_task = cursor.fetchall()
            valid_task = [ t[0] for t in valid_task ]
            different_item = set(data['tasks']).difference(set(valid_task))
            if different_item:
                return jsonify({'error': 'Invalid Task id', 'Tasks:': list(different_item)}), 400

            for task_id in data['tasks']:
                conn.execute('''
                INSERT INTO Sprint (round, name, project_id, due_date, task_id) values (?,?,?,?,?)''',
                             (data['round'], data['name'], data['project_id'], data['due_date'],task_id))
            conn.commit()
            return jsonify({'message': 'Sprint registered successfully'}), 200

    except Exception as e:
        print(str(e))
        return jsonify({'Error': str(e)}), 500
    finally:
        conn.close()

def delete_project(data):
    required_fields = ['project_id', 'creator_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    project_id = data['project_id']
    conn = get_db_connection()
    try:
        owner_id = get_owner_id(data['project_id'])
        if owner_id == -1:
            return jsonify({'error': 'No such project'}), 400

        if owner_id != data['creator_id']:
            return jsonify({'error': 'Owner ID mismatch'}), 400

        conn.execute('''DELETE FROM Projects WHERE project_id = ?''',
                     (project_id,))
        conn.execute('''DELETE FROM UserProject WHERE project_id = ?''',(project_id,))

        cursor = conn.cursor()
        cursor.execute('''SELECT task_id FROM ProjectTask WHERE ProjectTask.project_id = ?''', (project_id,))
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

        response=  jsonify({'message': 'Project deleted successfully'})

        # response.headers['Authorization'] = f'Bearer {access_token}'

        return response, 200 
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

def delete_task(data):
    required_fields = ['task_id', 'creator_id']
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

        cursor = conn.execute('SELECT project_id FROM ProjectTask WHERE task_id = ?',
                              (task_id,))
        project_id = cursor.fetchone()[0]

        owner_id = get_owner_id(project_id)

        if owner_id != data['creator_id']:
            return jsonify({'error': 'Owner ID mismatch'}), 400

        conn.execute('''DELETE FROM Tasks WHERE  task_id = ?''',
                     (task_id,))
        conn.execute('''DELETE FROM ProjectTask WHERE task_id = ?''',
                     (task_id,))
        conn.execute('''DELETE FROM UserTask WHERE task_id = ?''',
                     (task_id,))
        conn.execute('''DELETE FROM Sprint WHERE task_id = ?''',
                     (task_id,))
        conn.commit()

        return jsonify({'message': 'Task deleted successfully'}), 201
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

def delete_sprint(data):
    required_fields = ['round', 'project_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    round = data['round']
    project_id = data['project_id']
    owner_id = get_owner_id(project_id)
    conn = get_db_connection()
    try:
        cursor = conn.execute('SELECT * FROM Sprint WHERE round = ? and project_id = ?',
                              (round,project_id,))
        task = cursor.fetchone()
        if task is None:
            return jsonify({'error': 'No such Sprint'}), 400

        if owner_id != data['creator_id']:
            return jsonify({'error': 'Owner ID mismatch'}), 400

        conn.execute('''DELETE FROM Sprint WHERE  round = ? and project_id = ?''',
                     (round,project_id,))
        conn.commit()

        return jsonify({'message': 'Sprint deleted successfully'}), 201
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

def update_task(data):
    required_fields = ['task_id', 'creator_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    conn = get_db_connection()
    task_id = data['task_id']
    try:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM Tasks WHERE task_id = ?''',
                              (task_id,))
        task = cursor.fetchone()
        if task is None:
            return jsonify({'error': 'No such task'}), 400

        cursor = conn.execute('SELECT project_id FROM ProjectTask WHERE task_id = ?', (task_id,))
        project_id = cursor.fetchone()[0]

        owner_id = get_owner_id(project_id)
        cursor = conn.execute('SELECT user_id FROM UserTask WHERE task_id = ?', (task_id,))
        task_member_ids = cursor.fetchall()
        task_member_ids = [t[0] for t in task_member_ids]
        task_member_ids.append(owner_id)

        if data['creator_id'] not in task_member_ids:
            return jsonify({'error': 'Current user can not update task information'}), 400


        if 'user' in data.keys():
            if owner_id != data['creator_id']:
                return jsonify({'error': 'Owner ID mismatch'}), 400

            cursor = conn.cursor()
            cursor.execute('''SELECT user_id FROM UserTask WHERE task_id = ?''',
                                  (task_id,))
            id = cursor.fetchall()
            ids = [] # usrs in this task
            for item in id:
                ids.append(item[0])

            users_id = [] # users to operate
            invalid_name = []
            # through user_name get user_id
            for user in data['user']['users']:
                cursor = conn.execute('SELECT user_id FROM Users WHERE username = ?',
                                      (user,))
                i = cursor.fetchone()
                if i is None:
                    invalid_name.append(user)
                else:
                    users_id.append(i[0])

            if len(invalid_name) != 0:
                return jsonify({'err': 'Invalid user.', 'users:': invalid_name}), 400

            if data['user']['type'] == 'add':
                common_elements = set(ids) & set(users_id)
                if common_elements:
                    return jsonify({'err': 'user already exits.', 'user:': ids_to_names(list(common_elements))}), 400

                cursor = conn.cursor()
                cursor.execute('''SELECT user_id FROM UserProject WHERE project_id = ?''',
                               (project_id,))
                projectid = cursor.fetchall()
                project_ids = []  # user ids in project
                project_ids.append(owner_id)
                for item in projectid:
                    project_ids.append(item[0])
                different_elements = set(users_id).difference(set(project_ids))
                if different_elements:
                    return jsonify(
                        {'err': 'User not in porject.', 'users:': ids_to_names(list(different_elements))}), 400

                for user_id in users_id:
                    conn.execute('''INSERT INTO UserTask (user_id, task_id)
                                VALUES (?, ?)''',
                                 (user_id, task_id,))

            elif data['user']['type'] == 'remove':
                # different_elements = set(user_ids).difference(set(ids))
                # if different_elements:
                #     return jsonify(
                #         {'err': 'User not in porject.', 'users:': ids_to_names(list(different_elements))}), 400

                different_elements = set(users_id).difference(set(ids))
                if different_elements:
                    return jsonify({'err': 'user not exits in this project.','users:':ids_to_names(list(different_elements))}), 400
                for user_id in users_id:
                    conn.execute('''DELETE FROM UserTask WHERE  user_id = ? and task_id = ?''',
                                 (user_id, task_id,))
            else:
                return jsonify({'err': 'No such update task opration'}), 400

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

        conn.commit()
        return jsonify({'message': 'Task updated successfully'}), 201
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

def update_project(data):
    required_fields = ['project_id', 'creator_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    conn = get_db_connection()
    project_id = data['project_id']
    try:

        owner_id = get_owner_id(project_id)
        if owner_id == -1:
            return jsonify({'error': 'No such Project'}), 400

        if owner_id != data['creator_id']:
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
                         (data['replace_owner_id'], project_id,))
        conn.commit()
        response =  jsonify({'message': 'Project updated successfully'})

        return response, 200 
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

def update_sprint(data):
    required_fields = ['project_id', 'creator_id', 'round']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    conn = get_db_connection()
    project_id = data['project_id']
    round = data['round']
    try:
        owner_id = get_owner_id(project_id)
        if owner_id == -1:
            return jsonify({'error': 'No such Project'}), 400

        if owner_id != data['creator_id']:
            return jsonify({'error': 'Owner ID mismatch'}), 400

        cursor = conn.execute('SELECT * FROM Sprint WHERE round = ? and project_id = ?',
                              (round, project_id,))
        sprint = cursor.fetchone()
        if sprint is None:
            return jsonify({'error': 'No such Sprint'}), 400

        if 'name' in data.keys():
            conn.execute('''UPDATE Sprint
                                   SET name = ?
                                   WHERE round = ? and project_id = ?''',
                         (data['name'], round, project_id,))
        if 'new_round' in data.keys():
            conn.execute('''UPDATE Sprint
                                   SET round = ?
                                   WHERE round = ? and project_id = ?''',
                         (data['new_round'], round, project_id,))

        if 'start_at' in data.keys():
            conn.execute('''UPDATE Sprint
                                   SET start_at = ?
                                   WHERE round = ? and project_id = ?''',
                         (data['start_at'], round, project_id,))
        if 'due_date' in data.keys():
            conn.execute('''UPDATE Sprint
                                   SET due_date = ?
                                   WHERE round = ? and project_id = ?''',
                         (data['due_date'], round, project_id,))

        conn.commit()
        response = jsonify({'message': 'Project updated successfully'})

        return response, 200
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@pro_bp.route('/edit_sprint_task', methods=['POST'])
@jwt_required()
def edit_sprint_task():
    current_user = get_jwt_identity()['user_id']
    if request.method == "POST":
        data = request.get_json()
        required_fields = ['project_id', 'round', 'type', 'tasks']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        project_id = data['project_id']
        tasks = data['tasks']
        round = data['round']
        owner_id = get_owner_id(project_id)
        if owner_id == -1:
            return jsonify({'error': 'No such Project'}), 400

        if owner_id != current_user:
            return jsonify({'error': 'Owner ID mismatch'}), 400
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''SELECT name, start_at, due_date From Sprint WHERE project_id = ? and round = ?''', (project_id, round,))
            sprint = cursor.fetchone()
            if not sprint:
                return jsonify({'error': 'No such Sprint'}), 400

            cursor.execute('''SELECT task_id FROM ProjectTask WHERE project_id = ?''',
                           (project_id,))
            id = cursor.fetchall()
            ids = [i[0] for i in id] # task id in project

            if data['type'] == 'add':
                cursor.execute(''' SELECT task_id FROM  Sprint WHERE project_id = ?''', (project_id,))
                now_task_ids = cursor.fetchall()
                now_task_ids = [n[0] for n in now_task_ids]  # task id in sprint/ any sprint
                common_elements = set(now_task_ids) & set(tasks)
                if common_elements:
                    return jsonify({'err': 'Task already exits.', 'Task ids:': list(common_elements)}), 400


                for task_id in tasks:
                    conn.execute('''INSERT INTO Sprint (round, project_id, task_id, name, start_at, due_date) 
                                    VALUES (?, ?, ?,?,?,?)''',
                                 (round, project_id,task_id,sprint[0],sprint[1],sprint[2],))
                conn.commit()
                return jsonify({'msg': 'Added Sprint tasks Successfully'}), 200

            elif data['type'] == 'remove':
                cursor.execute(''' SELECT task_id
                                               FROM  Sprint
                                               WHERE project_id = ? and round = ?
                                           ''', (project_id,round,))
                now_task_ids = cursor.fetchall()
                now_task_ids = [n[0] for n in now_task_ids]  # task id in sprint/ any sprint

                different_elements = set(tasks).difference(set(now_task_ids))
                if different_elements:
                    return jsonify({'err': 'Tasks not exits in this sprint.', 'tasks:': list(different_elements)}), 400
                for task_id in tasks:
                    conn.execute('''DELETE FROM Sprint WHERE  round = ? and project_id = ? and task_id = ?''',
                                 (round, project_id,task_id,))
                conn.commit()
                return jsonify({'msg': 'Removed sprint tasks Successfully'}), 200

            else:
                return jsonify({'err': 'No such opration'}), 400
        except Exception as e:
            return jsonify(str(e))
        finally:
            conn.close()


@pro_bp.route('/sprint', methods=['POST', 'GET', 'DELETE', 'PUT'])
@jwt_required()
def sprint():
    current_user = get_jwt_identity()
    if request.method == "GET":
        args = request.args
        required_fields = ['project_id']
        if not all(field in args for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        return get_sprint(args)

    elif request.method == "POST":
        data = request.get_json()
        data['creator_id'] = current_user['user_id']
        response = register_sprint(data)
        return response

    elif request.method == "DELETE":
        data = request.get_json()
        data['creator_id'] = current_user['user_id']
        return delete_sprint(data)

    elif request.method == "PUT":
        data = request.get_json()
        data['creator_id'] = current_user['user_id']
        return update_sprint(data)

@pro_bp.route('/project_all', methods=['GET'])
def project_all():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(''' SELECT * FROM Projects p''')
        projects = cursor.fetchall()
        projects = [
            {'project_id': p[0], 'project_name': p[1], 'description': p[2], 'owner_id': p[3], 'created_at': p[4]} for p
            in projects]
        return projects
    except Exception as e:
        print(str(e))
    finally:
        conn.close()

@pro_bp.route('/edit_project_member', methods=['GET', 'POST'])
@jwt_required()
def edit_project_member():
    current_user = get_jwt_identity()['user_id']
    if request.method == "GET":
        args = request.args
        required_fields = ['project_id']
        if not all(field in args for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        project_id = args['project_id']

        owner_id = get_owner_id(project_id)
        if owner_id == -1:
            return jsonify({'error': 'No such Project'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
                                   SELECT username
                                   FROM  Users
                                   WHERE  user_id = ?
                               ''', (owner_id,))
        owner = cursor.fetchone()[0]

        cursor = conn.cursor()
        cursor.execute('''
                           SELECT username
                           FROM  Users u, UserProject up
                           WHERE up.project_id = ? and up.user_id = u.user_id
                       ''', (project_id,))
        all_users = cursor.fetchall()
        all_users = [ p[0] for p in all_users]
        all_users.append(owner)

        return jsonify({'users': all_users}), 200

    elif request.method == "POST":
        data = request.get_json()
        required_fields = ['project_id', 'type', 'users']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        project_id = data['project_id']
        owner_id = get_owner_id(project_id)
        if owner_id == -1:
            return jsonify({'error': 'No such Project'}), 400

        if owner_id != current_user:
            return jsonify({'error': 'Owner ID mismatch'}), 400

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''SELECT user_id FROM UserProject WHERE project_id = ?''',
                           (project_id,))
            id = cursor.fetchall()
            ids = [] # valid user id
            for item in id:
                ids.append(item[0])

            user_ids = []
            invalid_name = []
            # through user_name get user_id
            for user in data['users']:
                cursor = conn.execute('SELECT user_id FROM Users WHERE username = ?',
                                      (user,))
                i = cursor.fetchone()
                if i is None:
                    invalid_name.append(user)
                else:
                    user_ids.append(i[0])

            if len(invalid_name) != 0:
                return jsonify({'err': 'User not exits.', 'users:': invalid_name}), 400

            if owner_id in user_ids:
                return jsonify({'err': 'Cannot add/remove the project owner.'}), 400

            if data['type'] == 'add':
                common_elements = set(ids) & set(user_ids)
                if common_elements:
                    return jsonify({'err': 'user already exits.', 'users:': ids_to_names(list(common_elements))}), 400

                cursor = conn.execute('SELECT user_id FROM UserProject WHERE project_id = ?',
                                      (project_id,))


                for user_id in user_ids:
                    conn.execute('''INSERT INTO UserProject (user_id, project_id) VALUES (?, ?)''',
                                 (user_id, project_id,))
                conn.commit()
                return jsonify({'msg': 'Added project members Successfully'}), 200

            elif data['type'] == 'remove':
                different_elements = set(user_ids).difference(set(ids))
                if different_elements:
                    return jsonify({'err': 'user not exits in this project.', 'users:': ids_to_names(list(different_elements))}), 400
                for user_id in user_ids:
                    conn.execute('''DELETE FROM UserProject WHERE  user_id = ? and project_id = ?''',
                                 (user_id, project_id,))
                    conn.execute('''DELETE FROM UserTask
                                    WHERE  user_id = ?
                                    and task_id in (select pt.task_id from ProjectTask pt, UserTask ut
                                                    where ut.user_id = ?
                                                    and pt.project_id = ?
                                                    and pt.task_id = ut.task_id);''',
                                 (user_id, user_id, project_id,))
                conn.commit()
                return jsonify({'msg': 'Removed project members Successfully'}), 200
            else:
                return jsonify({'err': 'No such opration'}), 400
        except Exception as e:
            print(str(e))
        finally:
            conn.close()

# This page show all task of one task and can register task
@pro_bp.route('/project_detail', methods=['POST', 'GET', 'DELETE', 'PUT'])
@jwt_required() 
def project_detail():
    # 用户注册、更新任务
    current_user = get_jwt_identity()
    if request.method == "GET":
        args = request.args
        required_fields = ['project_id']
        if not all(field in args for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        return get_project_detail(args)

    elif request.method == "POST":
        data = request.get_json()
        data['creator_id'] = current_user['user_id']
        response = register_task(data)
        return response

    elif request.method == "DELETE":
        data = request.get_json()
        data['creator_id'] = current_user['user_id']
        return delete_task(data)

    elif request.method == "PUT":
        data = request.get_json()
        data['creator_id'] = current_user['user_id']
        return update_task(data)


# This page show all project and tasks of one user and can register project
@pro_bp.route('/project', methods=['POST', 'GET', 'DELETE', 'PUT'])
@jwt_required()
def project():
    # 用户注册、更新项目
    current_user = get_jwt_identity()   # This will return the identity you set when creating the token
    if request.method == "GET":

        all_project = get_user_project(current_user['user_id'])
        all_own_project = get_own_project(current_user['user_id'])
        all_tasks = get_user_tasks(current_user['user_id'])

        response = jsonify({'message': 'show all project successfully',
                        'project_belong': all_project,
                        'tasks': all_tasks,
                        'own_project': all_own_project
                        })
        return response, 200 
    

    elif request.method == "POST":
        data = request.get_json()
        data['creator_id'] = current_user['user_id']
        return register_project(data)

    elif request.method == "DELETE":
        data = request.get_json()
        data['creator_id'] = current_user['user_id']
        return delete_project(data)

    elif request.method == "PUT":
        data = request.get_json()
        data['creator_id'] = current_user['user_id']
        return update_project(data)


@pro_bp.route('/some-protected-route', methods=['GET'])
@jwt_required()  # This decorator ensures that the user is authenticated
def protected_route():
    # Get the current user's identity from the JWT token
    current_user = get_jwt_identity()  # This will return the identity you set when creating the token
    user_id = current_user['user_id']  # Extract user_id from the identity

    return jsonify({
        'message': 'Access granted',
        'user_id': user_id,
        'username': current_user
    }), 200