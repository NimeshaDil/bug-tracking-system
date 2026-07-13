from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config import config
from app.models import db, User
import os
import logging

login_manager = LoginManager()
logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            logger.error(f"Error loading user {user_id}: {str(e)}")
            return None
    
    with app.app_context():
        try:
            db.create_all()
            seed_default_users()
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
        
        from app.routes.auth import auth_bp
        from app.routes.bugs import bugs_bp
        from app.routes.dashboard import dashboard_bp
        from app.routes.users import users_bp
        
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(bugs_bp, url_prefix='/bugs')
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
        app.register_blueprint(users_bp, url_prefix='/users')
        
        @app.route('/')
        def index():
            return redirect(url_for('dashboard.dashboard'))
    
    return app

def seed_default_users():
    if User.query.first() is not None:
        return
    
    users = [
        {'email': 'admin@example.com', 'username': 'admin', 'password': 'password123', 'role': 'admin'},
        {'email': 'dev@example.com', 'username': 'developer', 'password': 'password123', 'role': 'developer'},
        {'email': 'tester@example.com', 'username': 'tester', 'password': 'password123', 'role': 'tester'},
    ]
    
    for user_data in users:
        user = User(email=user_data['email'], username=user_data['username'], role=user_data['role'], is_active=True)
        user.set_password(user_data['password'])
        db.session.add(user)
    
    db.session.commit()
