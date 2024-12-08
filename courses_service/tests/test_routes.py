import pytest
from unittest.mock import patch
from app import create_app, db

@pytest.fixture
def client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # Создадим тестовый курс
            from app.models import Course
            course = Course(
                title='Test Course',
                description='Test Description',
                instructor_id=1
            )
            db.session.add(course)
            db.session.commit()
            
        yield client

@patch('requests.post')
def test_get_courses(mock_post, client):
    # Мокаем ответ от users service
    mock_response = type('Response', (), {
        'ok': True,
        'json': lambda: {
            'valid': True,
            'user': {
                'id': 1,
                'username': 'testuser',
                'email': 'test@example.com'
            }
        }
    })
    mock_post.return_value = mock_response
    
    auth_header = {'Authorization': 'Bearer test_token'}
    response = client.get('/courses', headers=auth_header)
    
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(x['title'] == 'Test Course' for x in data)