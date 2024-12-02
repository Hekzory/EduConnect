import sys
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
import requests
import os
from .models import User
from flask import current_app as app

bp = Blueprint('main', __name__)

USERS_SERVICE = os.getenv('USERS_SERVICE_URL')
COURSES_SERVICE = os.getenv('COURSES_SERVICE_URL')
TASKS_SERVICE = os.getenv('TASKS_SERVICE_URL')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        response = requests.post(f'{USERS_SERVICE}/login', json={
            'username': request.form['username'],
            'password': request.form['password']
        })
        if response.ok:
            data = response.json()
            user = User(data['user'])
            session['token'] = data['token']  # Store token in session
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid credentials')
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    session.pop('token', None)  # Remove token from session
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        response = requests.post(f'{USERS_SERVICE}/register', json={
            'username': request.form['username'],
            'email': request.form['email'],
            'password': request.form['password']
        })
        if response.ok:
            data = response.json()
            user = User(data['user'])
            session['token'] = data['token']  # Store token in session
            login_user(user)
            flash('Registration successful!')
            return redirect(url_for('main.index'))
        flash('Registration failed: ' + response.json().get('message', 'Unknown error'))
    return render_template('register.html')

def get_auth_headers() -> dict[str, str]:
    token = session.get('token')
    return {'Authorization': f'Bearer {token}'} if token else {}

@bp.route('/')
def index():
    response = requests.get(f'{COURSES_SERVICE}/courses', headers=get_auth_headers())
    print(str(response.text), file=sys.stderr)
    courses = response.json() if response.ok else []
    return render_template('index.html', courses=courses)

@bp.route('/course/<int:course_id>')
@login_required
def course_detail(course_id):
    course_response = requests.get(
        f'{COURSES_SERVICE}/courses/{course_id}',
        headers=get_auth_headers()
    )
    tasks_response = requests.get(
        f'{TASKS_SERVICE}/tasks/{course_id}',
        headers=get_auth_headers()
    )
    
    if not course_response.ok:
        flash('Failed to load course details')
        return redirect(url_for('main.index'))
        
    course = course_response.json()
    tasks = tasks_response.json() if tasks_response.ok else []
    return render_template('course_detail.html', course=course, tasks=tasks)

@bp.route('/submit_task/<int:task_id>', methods=['POST'])
@login_required
def submit_task(task_id):
    response = requests.post(
        f'{TASKS_SERVICE}/submit/{task_id}',
        headers=get_auth_headers(),
        json={
            'content': request.form['content']
        }
    )
    if response.ok:
        flash('Task submitted successfully!')
    else:
        flash('Submission failed: ' + response.json().get('message', 'Unknown error'))
    return redirect(url_for('main.course_detail', course_id=request.form['course_id']))

# Add error handlers
@bp.errorhandler(401)
def unauthorized_error(error):
    logout_user()
    session.pop('token', None)
    flash('Please log in to access this page')
    return redirect(url_for('main.login'))

@bp.errorhandler(403)
def forbidden_error(error):
    flash('You do not have permission to access this resource')
    return redirect(url_for('main.index'))