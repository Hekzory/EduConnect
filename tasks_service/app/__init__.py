from datetime import datetime, timedelta, UTC
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config=None):
    app = Flask(__name__)
    app.debug = True
    if config is None:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
        app.config['SECRET_KEY'] = 'your-secret-key'  # In production, use proper secret key
    elif config:
        app.config.update(config)
    
    db.init_app(app)
    
    from .routes import bp
    app.register_blueprint(bp)
    
    with app.app_context():
        db.create_all()

        from .models import Task
        # Добавим начальные задачи
        if Task.query.count() < 2:
            task1 = Task(
                course_id=1,
                title='Первая задача',
                description='Описание первой задачи',
                deadline=datetime.now(UTC) + timedelta(days=7)
            )
            task2 = Task(
                course_id=1,
                title='Вторая задача',
                description='Описание первой задачи',
                deadline=datetime.now(UTC) - timedelta(days=7)
            )
            db.session.add(task1)
            db.session.add(task2)
            db.session.commit()
    
    return app