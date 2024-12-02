from datetime import datetime, timedelta
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    
    db.init_app(app)
    
    from .routes import bp
    app.register_blueprint(bp)
    
    with app.app_context():
        db.create_all()

        from .models import Task
        # Добавим начальные задачи
        if Task.query.count() == 0:
            task1 = Task(
                course_id=1,  # Укажите ID курса
                title='Первая задача',
                description='Описание первой задачи',
                deadline=datetime.utcnow() + timedelta(days=7)
            )
            db.session.add(task1)
            db.session.commit()
    
    return app