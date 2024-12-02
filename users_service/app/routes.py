from flask import Blueprint, request, jsonify
from .models import User, db
from sqlalchemy.exc import IntegrityError
from .auth import generate_token, token_required, decode_token

bp = Blueprint('users', __name__)

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already registered'}), 400
            
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        # Generate token for immediate login after registration
        token = generate_token(user.id)
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Database error occurred'}), 500
    except KeyError:
        return jsonify({'message': 'Missing required fields'}), 400

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            token = generate_token(user.id)
            return jsonify({
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
        return jsonify({'message': 'Invalid credentials'}), 401
    except KeyError:
        return jsonify({'message': 'Missing required fields'}), 400

@bp.route('/users/me', methods=['GET'])
@token_required
def get_current_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })

@bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user_id, user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })

@bp.route('/verify-token', methods=['POST'])
def verify_token():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'valid': False}), 401
        
        token = auth_header.split(" ")[1]
        user_id = decode_token(token)
        
        if user_id is None:
            return jsonify({'valid': False}), 401
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'valid': False}), 401
            
        return jsonify({
            'valid': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    except Exception:
        return jsonify({'valid': False}), 401