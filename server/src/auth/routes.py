import os
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime, timezone
from flask_jwt_extended import (
    get_jwt,
    unset_jwt_cookies,
    create_access_token, 
    jwt_required, 
    get_jwt_identity,
    JWTManager   
)

auth_bp = Blueprint('auth', __name__)

# Store for blacklisted tokens (in production, use Redis or database)
jwt_blacklist = set()
jwt = JWTManager()  # Add this line

def get_db_connection():
    try: 
        DB_PATH = os.path.abspath(os.path.join(os.getcwd(), 'database', 'test.db'))
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise

# Add this function to check if a token is blacklisted
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    try:
        jti = jwt_payload["jti"]
        conn = get_db_connection()
        cursor = conn.execute('SELECT id FROM BlacklistedTokens WHERE jti = ?',
                              (jti, ))
        is_blacklisted = cursor.fetchone() is not None
        conn.close()
        return is_blacklisted
    except Exception as e:
        print(f"Error checking blacklist: {e}")
        return True  # Fail secure - if we can't check, assume token is blacklisted


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)

    # Validate required fields
    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Add password complexity check
    password = data['password']
    if not is_password_complex(password):
        return jsonify({
            'error':
            'Password must be at least 6 characters long and contain at least one letter and one number.'
        }), 400

    username = data['username']
    email = data['email']

    if isinstance(username, str):
        username = username.encode('utf-8').decode(
            'utf-8')  # Ensure UTF-8 encoding
    if isinstance(email, str):
        email = email.encode('utf-8').decode('utf-8')  # Ensure UTF-8 encoding

    conn = get_db_connection()
    try:
        # Check if user already exists

        cursor = conn.execute(
            'SELECT * FROM Users WHERE username = ? OR email = ?',
            (username, email))  # Encode to UTF-8
        if cursor.fetchone():
            return jsonify({'error': 'Username or email already exists'}), 409

        # Create new user
        password_hash = generate_password_hash(data['password'],
                                               method='pbkdf2')
        conn.execute('''
            INSERT INTO Users (username, email, password)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))  # Encode to UTF-8
        conn.commit()

        return jsonify({'message': 'User registered successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# Add this helper function to check password complexity
def is_password_complex(password):
    import re
    # Check for at least 6 characters, at least one letter, and one number
    return bool(re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', password))


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)

    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400

    username = data['username']
    if isinstance(username, str):
        username = username.encode('utf-8').decode(
            'utf-8')  # Ensure UTF-8 encoding

    conn = get_db_connection()
    try:
        # Update the query to check for both username and email
        cursor = conn.execute('''
            SELECT user_id, username, email, password 
            FROM Users 
            WHERE username = ? OR email = ?
        ''', (username, username))  # Check both username and email
        user = cursor.fetchone()

        # Convert tuple to dictionary for easier access
        if user:
            user_dict = {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'password': user[3]
            }

            if check_password_hash(user_dict['password'], data['password']):
                # Create JWT token
                access_token = create_access_token(
                    identity={
                        'user_id': user_dict['user_id'],
                        'username': user_dict['username'],
                    })

                response = jsonify({
                    'message': 'User login successfully',
                    'user': {
                        'username': user_dict['username'],
                        'email': user_dict['email']
                    },
                    'token': access_token
                })
                response.headers['Authorization'] = f'Bearer {access_token}'
                return response, 200

        return jsonify({'error': 'Invalid credentials'}), 401

    finally:
        conn.close()


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        # Get JWT claims
        jwt_data = get_jwt()
        jti = jwt_data["jti"]
        exp = jwt_data["exp"]

        conn = get_db_connection()
        try:
            # Store the blacklisted token
            conn.execute(
                '''
                INSERT INTO BlacklistedTokens (jti, expiry)
                VALUES (?, ?)
            ''', (jti, datetime.fromtimestamp(exp)))
            conn.commit()

            response = jsonify({'message': 'Successfully logged out'})
            unset_jwt_cookies(response)
            return response, 200

        finally:
            conn.close()

    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_profile():
    try:
        # Check if token is blacklisted
        jwt_data = get_jwt()
        jti = jwt_data["jti"]

        conn = get_db_connection()
        cursor = conn.execute('SELECT id FROM BlacklistedTokens WHERE jti = ?',
                              (jti, ))
        if cursor.fetchone() is not None:
            conn.close()
            return jsonify({'error': 'Token has been revoked'}), 401

        current_user = get_jwt_identity()
        user_id = current_user.get('user_id')

        cursor = conn.execute(
            '''
            SELECT user_id, username, email
            FROM Users 
            WHERE user_id = ?
        ''', (user_id, ))
        user = cursor.fetchone()
        conn.close()

        if user is None:
            return jsonify({'error': 'User not found'}), 404

        # Convert tuple to dictionary
        user_dict = {'user_id': user[0], 'username': user[1], 'email': user[2]}

        return jsonify({
            'message': 'User retrieval successfully',
            'user': user_dict
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve profile: {str(e)}'}), 500


# For Testing
@auth_bp.route('/test-db-connection', methods=['GET'])
def test_db_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        return jsonify({
            'message':
            f'Database connection successful , Here is DB table : {tables}'
        }), 200
    except Exception as e:
        return jsonify({'error':
                        f'Database connection failed: {str(e)}.'}), 500


# For Testing
@auth_bp.route('/users', methods=['GET'])
def get_all_users():
    try:
        conn = get_db_connection()
        cursor = conn.execute('''
            SELECT user_id, username, email 
            FROM Users 
            ORDER BY user_id
        ''')
        users = cursor.fetchall()
        conn.close()

        # Convert tuples to dictionaries
        users_list = [
            {
                'user_id':
                user[0],
                'username':
                user[1].decode('utf-8')
                if isinstance(user[1], bytes) else user[1],  # Decode if bytes
                'email':
                user[2].decode('utf-8')
                if isinstance(user[2], bytes) else user[2]  # Decode if bytes
            } for user in users
        ]

        return jsonify({
            'message': 'All user retrieval successful',
            'users': users_list,
            'total': len(users_list)
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve users: {str(e)}'}), 500
