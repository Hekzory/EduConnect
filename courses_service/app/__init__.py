import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config=None):
    app = Flask(__name__)
    if config is None:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    elif config:
        app.config.update(config)
    
    db.init_app(app)
    
    from .routes import bp
    app.register_blueprint(bp)
    
    with app.app_context():
        db.create_all()
        
        from .models import Course
        # Добавим начальные курсы
        if Course.query.count() == 0:
            course1 = Course(
                title='Основы программирования',
                description='Введение в программирование на Python',
                instructor_id=1  # Замените на корректный ID инструктора
            )
            db.session.add(course1)
            db.session.commit()
    
    return app