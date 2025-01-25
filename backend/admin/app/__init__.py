# admin/app/__init__.py
import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from flask_pymongo import PyMongo
from flask_login import LoginManager, current_user
from bson.objectid import ObjectId

# Load environment variables
load_dotenv()

# Initialize extensions
mongo = PyMongo()
login_manager = LoginManager()

# Create a dummy db object to match SQLAlchemy interface
class DummyDB:
    class Model:
        pass
    
    def init_app(self, app):
        pass

db = DummyDB()

def create_app():
    app = Flask(__name__)
    
    # Configuration from environment variables
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize extensions
    mongo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Configure upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from .routes import auth, categories, documents
    app.register_blueprint(auth.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(documents.bp)

    # Add root route
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('categories.index'))
        return redirect(url_for('auth.login'))

    # Setup login manager
    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        return User(user_data) if user_data else None

    # Create default admin user
    with app.app_context():
        create_default_admin()

    return app

def create_default_admin():
    from werkzeug.security import generate_password_hash
    users = mongo.db.users
    
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_password = os.getenv('ADMIN_PASSWORD')
    
    admin = users.find_one({'username': admin_username})
    if not admin:
        # Create new admin user
        users.insert_one({
            'username': admin_username,
            'password': generate_password_hash(admin_password),
            'is_admin': True
        })
        print('Default admin user created')
    else:
        # Update existing admin's password if hash format is incorrect
        if not admin['password'].startswith('pbkdf2:sha256:'):
            users.update_one(
                {'_id': admin['_id']},
                {'$set': {
                    'password': generate_password_hash(admin_password),
                    'is_admin': True
                }}
            )
            print('Admin password hash updated')