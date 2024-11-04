# API 接口


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