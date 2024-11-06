# API 接口

Local   : http://localhost:8000/

Replite : https://8a74705f-88cc-40ba-af38-3379f495a983-00-1npdqf5pljqau.pike.replit.dev/

## Sign Up Example
```
curl -X POST http://localhost:8000/auth/register \
-H "Content-Type: application/json" \
-d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}'
```

#### Output
> {'message': 'User registered successfully'}


## Login Example
```
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
-H "Content-Type: application/json" \
-d '{"username": "testuser", "password": "password123"}' \
| jq -r '.access_token')

echo $TOKEN
```

#### Output
> {'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTczMDcwMDM0OCwianRpIjoiYjc3ZTE3NTQtYTlmMS00MGFhLTlmOGUtZWY1ZjBiN2NjNmE2IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6InRlc3R1c2VyIn0sIm5iZiI6MTczMDcwMDM0OCwiY3NyZiI6ImE4Y2ZjZTQzLWNhYmUtNGE3MC1hN2VkLWFlZjI5YmI4YzY1OSIsImV4cCI6MTczMDc4Njc0OH0.Uw8jCU7X4bP0Zj3CqZT5zHPUwg_qX2f_GBVAitc2pzo','message': 'User login successfully', 'user': {'email': 'test@example.com', 'username': 'testuser'}}


## Logout Example
```
# 1. Login and save token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
-H "Content-Type: application/json" \
-d '{"username": "testuser", "password": "password123"}' \
| jq -r '.access_token')

# 2. Logout using the token
curl -X POST http://localhost:8000/auth/logout \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json"
```

#### Output
> {'message': 'Successfully logged out'}

## Retrieval users profile for testing authorization token(For development/testing usage)

```
# 1. Login and save token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
-H "Content-Type: application/json" \
-d '{"username": "testuser", "password": "password123"}' \
| jq -r '.access_token')

# 2. Get profile using the token
curl -X GET http://localhost:8000/auth/me \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json"
```
#### Output
> {'message': 'User retrieval successfully', 'user': {'email': 'test@example.com', 'user_id': 1, 'username': 'testuser'}}


## Create Project

```
curl -X POST http://localhost:8000/pro/project \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <your_token_here>" \
     -d '{
           "project_name": "DE Project",
           "description": "This is a DE project"
         }'
```

#### Output

>{'message': 'Project registered successfully','owner_id': 1,'project_name':'DE Project'})




## Retrieval All users profile (For development/testing usage)
```
curl -X GET http://localhost:8000/auth/users
```
#### Output
> {'message': 'All user retrieval successful', 'total': 1, 'users': [{'email': 'test@example.com', 'user_id': 1, 'username': 'testuser'}]}