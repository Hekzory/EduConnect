import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SECRET_KEY'] = 'your-secret-key'  # In production, use proper secret key
    
    db.init_app(app)
    
    from .routes import bp
    app.register_blueprint(bp)
    
    with app.app_context():
        db.create_all()
        
        from .models import User
        if User.query.count() == 0:
            user = User(username='admin', email='admin@example.com')
            user.set_password('admin')
            db.session.add(user)
            db.session.commit()
    
    return app