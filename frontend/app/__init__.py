from flask import Flask
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv
load_dotenv()
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    
    # Initialize MongoDB
    mongo.init_app(app)
    
    # Create uploads directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from .routes import main
    app.register_blueprint(main.bp)
    
    # Initialize template filters
    from .utils.template_filters import init_filters
    init_filters(app)
    
    return app