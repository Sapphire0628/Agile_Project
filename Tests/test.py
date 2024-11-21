import unittest
import json
import requests



class TestUser(unittest.TestCase):
    def setUp(self):
        self.auth = 'http://localhost:8000//auth/'
        self.token = ''

    def test_1register(self):
        data = {
                "username": "Ada212",
                "email": "ada211@gmail.com",
                "password": "Ada123"
            }
        response = requests.post(self.auth + "/register", json=data)
        self.assertEqual(201, response.status_code)

    def test_2login(self):
        data = {
            "username": "Ada2",
            "password": "Ada123"
        }
        response = requests.post(self.auth + 'login', json=data)
        self.assertEqual(200, response.status_code)
        self.token = response.json()['token']

    def test_3logout(self):
        self.test_2login()

        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        response = requests.post(
            self.auth + 'logout',
            headers=headers
        )
        self.assertEqual(200, response.status_code)

class TestProject(unittest.TestCase):
    def setUp(self):
        self.pro = 'http://localhost:8000//pro/'
        data = {
            "username": "Ada2",
            "password": "Ada123"
        }
        response = requests.post('http://localhost:8000//auth/' + 'login', json=data)
        token = response.json()['token']
        self.headers = {
            "Authorization": f"Bearer {token}"
        }

    def test_1create(self):
        data = {
            "project_name": "project_test_1",
            'project_id' : 13
        }
        response = requests.post(self.pro + 'project', json=data, headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_2edit_member(self):
        data = {
            'type': 'add',  # 或者remove或者update
            'project_id': 13,
            "users": [{'name': 'Ada21',
                       # 'role':'Tester'
                       }]}
        response = requests.post(self.pro + 'edit_project_member', json=data, headers=self.headers)
        self.assertEqual(200, response.status_code)
        data = {
            'type': 'remove',  # 或者remove或者update
            'project_id': 13,
            "users": [{'name': 'Ada21',
                       # 'role':'Tester'
                       }]}
        response = requests.post(self.pro + 'edit_project_member', json=data, headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_5delete(self):
        data = {
            "project_id": 13
        }
        response = requests.delete(self.pro + 'project', json=data, headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_3get_information(self):
        response = requests.get(self.pro + 'project' + "?13", headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_4get_project_member(self):
        response = requests.get(self.pro + 'edit_project_member' + "?project_id=13", headers=self.headers)
        self.assertEqual(200, response.status_code)

class TestTask(unittest.TestCase):
    def setUp(self):
        self.pro = 'http://localhost:8000//pro/'
        data = {
            "username": "Ada2",
            "password": "Ada123"
        }
        response = requests.post('http://localhost:8000//auth/' + 'login', json=data)
        token = response.json()['token']
        self.headers = {
            "Authorization": f"Bearer {token}"
        }

    def test_1create(self):
        data = {
            "project_id": 16,  # 在project_id项目创建
            "task_name": "test_task_name1",
            "status": "Not start",
            "priority": 2,
            "due_date": '2024-11-4',
            # "users": ['Ada2']  # should be username list 注意这里的成员要是project里的成员
        }
        response = requests.post(self.pro + 'project_detail', json=data, headers=self.headers)
        self.assertEqual(201, response.status_code)

    def test_2edit_member(self):
        data = {
            # 'task_name': 'updated_name', #可选
            # 'description' : 'updated_description', #可选
            'status': 'Done',  # 可选
            # 'priority': 'High', #可选
            # 'due_date': '2011-11-1', #可选
            'task_id': 7,
            'user': {  # 注意这里的成员要是project里的成员，但是我后端没写判断，希望你不要传一些奇怪的东西
                'type': 'add',  # 里面是 'add' or 'remove'
                'users': ['Ada21']  # 里面是username
            },  # 可选
        }
        response = requests.put(self.pro + 'project_detail', json=data, headers=self.headers)
        self.assertEqual(201, response.status_code)
        data = {
            # 'task_name': 'updated_name', #可选
            # 'description' : 'updated_description', #可选
            'status': 'Done',  # 可选
            # 'priority': 'High', #可选
            # 'due_date': '2011-11-1', #可选
            'task_id': 7,
            'user': {
                'type': 'remove',  # 里面是 'add' or 'remove'
                'users': ['Ada21']  # 里面是username
            },  # 可选
        }
        response = requests.put(self.pro + 'project_detail', json=data, headers=self.headers)
        self.assertEqual(201, response.status_code)

    def test_3delete(self):
        data = {
            'task_id': 16,
        }
        response = requests.delete(self.pro + 'project_detail', json=data, headers=self.headers)
        self.assertEqual(201, response.status_code)

class TestSprint(unittest.TestCase):
    def setUp(self):
        self.pro = 'http://localhost:8000//pro/'
        data = {
            "username": "Ada2",
            "password": "Ada123"
        }
        response = requests.post('http://localhost:8000//auth/' + 'login', json=data)
        token = response.json()['token']
        self.headers = {
            "Authorization": f"Bearer {token}"
        }

    def test_1create(self):
        data = {
            'name': 'test',  # 必须
            'project_id': 16,  # 必须
            'round': 1,  # 默认0
            # 'due_date':'2011-11-1', #默认 null
            # 'tasks': [5], #默认 null   记得传list
        }
        response = requests.post(self.pro + 'sprint', json=data, headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_2edit_task(self):
        data = {
            'project_id': 16,  # 必须
            'round': 1,  # 必须
            'type': 'add',  # or remove
            'tasks': [1, 2, 3]
        }
        response = requests.post(self.pro + 'edit_sprint_task', json=data, headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_3update(self):
        data = {
            'project_id': 16,  # 必须
            'round': 1,  # 必须
            'new_round': 4,
            'name': 'test_update',
            'start_at': '2011-11-2',
            'due_date': '2011-11-2',  # 默认 null
        }
        response = requests.put(self.pro + 'sprint', json=data, headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_4delete(self):
        data = {
            'project_id': 16,  # 必须
            'round': 4,  # 必须
        }
        response = requests.delete(self.pro + 'sprint', json=data, headers=self.headers)
        self.assertEqual(201, response.status_code)

class TestComment(unittest.TestCase):
    def setUp(self):
        self.pro = 'http://localhost:8000//pro/'
        data = {
            "username": "Ada2",
            "password": "Ada123"
        }
        response = requests.post('http://localhost:8000//auth/' + 'login', json=data)
        token = response.json()['token']
        self.headers = {
            "Authorization": f"Bearer {token}"
        }

    def test_1create(self):
        data = {
            'task_id': 7,
            'comment': '???test',
        }
        response = requests.post(self.pro + 'comment', json=data, headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_2get(self):
        response = requests.get(self.pro + 'comment?task_id=7', headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_3update(self):
        data = {
            'comment_id': 7,
            'comment': '1',
        }
        response = requests.put(self.pro + 'comment', json=data, headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_4delete(self):
        data = {
            'comment_id': 7,
        }
        response = requests.delete(self.pro + 'comment', json=data, headers=self.headers)
        self.assertEqual(200, response.status_code)









if __name__ == '__main__':
    unittest.main()