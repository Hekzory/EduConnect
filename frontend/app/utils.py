from functools import wraps
from flask import session, redirect, url_for, flash
import requests

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def make_request(method, url, **kwargs):
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        flash(f"Service temporarily unavailable: {str(e)}")
        return None