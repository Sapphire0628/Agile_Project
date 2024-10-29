import os
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from flask_jwt_extended import (
    create_access_token, 
    jwt_required, 
    get_jwt_identity   
)

auth_bp = Blueprint('auth', __name__)

def get_db_connection():
    try: 
        DB_PATH = os.path.abspath(os.path.join(os.getcwd(), 'database', 'test.db'))
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise



@auth_bp.route('/test-db-connection', methods=['GET'])
def test_db_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        return jsonify({'message': f'Database connection successful , Here is DB table : {tables}'}), 200
    except Exception as e:
        return jsonify({'error': f'Database connection failed: {str(e)}.'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    try:
        # Check if user already exists
        cursor = conn.execute('SELECT * FROM Users WHERE username = ? OR email = ?',
                            (data['username'], data['email']))
        if cursor.fetchone():
            return jsonify({'error': 'Username or email already exists'}), 409
        
        # Create new user
        password_hash = generate_password_hash(data['password'])
        conn.execute('''
            INSERT INTO Users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', (data['username'], data['email'], password_hash, 'user'))
        conn.commit()
        
        return jsonify({'message': 'User registered successfully'}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    conn = get_db_connection()
    try:
        cursor = conn.execute('SELECT * FROM Users WHERE username = ?', 
                            (data['username'],))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password_hash'], data['password']):
            # Create JWT token
            access_token = create_access_token(identity={
                'user_id': user['user_id'],
                'username': user['username'],
                'role': user['role']
            })
            return jsonify({
                'access_token': access_token,
                'user': {
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role']
                }
            }), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    finally:
        conn.close()

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_profile():
    current_user = get_jwt_identity()
    return jsonify(current_user), 200