import pytest
from app import create_app, db

@pytest.fixture
def client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_register(client):
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password'
    })
    assert response.status_code == 201
    assert response.get_json()['message'] == 'User created successfully'

def test_login(client):
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password'
    })
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'password'
    })
    assert response.status_code == 200
    assert 'token' in response.get_json()

def test_invalid_login(client):
    response = client.post('/login', json={
        'username': 'nonexistent',
        'password': 'wrong'
    })
    assert response.status_code == 401
    assert 'Invalid credentials' in response.get_json()['message']

def test_verify_token(client):
    # First register and login to get a token
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password'
    })
    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'password'
    })
    token = login_response.get_json()['token']
    
    # Test token verification
    response = client.post('/verify-token', 
        headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['valid'] is True
    assert data['user']['username'] == 'testuser'

def test_verify_invalid_token(client):
    response = client.post('/verify-token',
        headers={'Authorization': 'Bearer invalid_token'})
    assert response.status_code == 401
    assert response.get_json()['valid'] is False

def test_get_current_user(client):
    # Register and login first
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password'
    })
    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'password'
    })
    token = login_response.get_json()['token']
    
    # Test getting current user
    response = client.get('/users/me',
        headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    user = response.get_json()
    assert user['username'] == 'testuser'
    assert user['email'] == 'test@example.com'

def test_register_duplicate_username(client):
    # Register first user
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test1@example.com',
        'password': 'password'
    })
    
    # Try to register with same username
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'test2@example.com',
        'password': 'password'
    })
    assert response.status_code == 400
    assert 'Username already exists' in response.get_json()['message']