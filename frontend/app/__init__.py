from flask import Flask
from flask_login import LoginManager
import os

login_manager = LoginManager()

def create_app(config=None):
    app = Flask(__name__)
    if config is None:
        app.config['SECRET_KEY'] = 'your-secret-key'  # In production, use proper secret key
    elif config:
        app.config.update(config)
    
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    from .models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)
    
    from .routes import bp
    app.register_blueprint(bp)
    
    return app