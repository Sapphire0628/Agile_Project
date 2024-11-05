import os 
from dotenv import load_dotenv

from flask import Flask
from flask_jwt_extended import JWTManager
from auth.routes import auth_bp
from Project.Project import pro_bp
import datetime


load_dotenv()

app = Flask(__name__)
# NEVER hardcode the secret key in production!
# Use environment variables or a secure configuration management system
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Change this to a secure secret key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

jwt = JWTManager(app)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(pro_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)