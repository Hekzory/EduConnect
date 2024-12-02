from flask_login import UserMixin
import requests
import os

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.token = user_data.get('token')

    @staticmethod
    def get(user_id):
        from flask import session
        token = session.get('token')
        if not token:
            return None
            
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(
                f"{os.getenv('USERS_SERVICE_URL')}/users/{user_id}",
                headers=headers
            )
            if response.ok:
                return User(response.json())
        except:
            return None
        return None