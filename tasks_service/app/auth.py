from functools import wraps
from flask import request, jsonify
import os
import requests

JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')  # Use same secret as users service
USERS_SERVICE = os.getenv('USERS_SERVICE_URL')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        # Verify token with users service
        try:
            response = requests.post(
                f'{USERS_SERVICE}/verify-token',
                headers={'Authorization': f'Bearer {token}'}
            )
            if not response.ok:
                return jsonify({'message': 'Invalid token'}), 401
                
            user_data = response.json()['user']
            return f(user_data, *args, **kwargs)
        except requests.exceptions.RequestException:
            return jsonify({'message': 'Authentication service unavailable'}), 503

    return decorated