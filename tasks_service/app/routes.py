from flask import Blueprint, request, jsonify
from .models import Task, Submission, db
from .auth import token_required
from datetime import datetime

bp = Blueprint('tasks', __name__)

@bp.route('/tasks/<int:course_id>', methods=['GET'])
@token_required
def get_tasks(current_user, course_id):
    tasks = Task.query.filter_by(course_id=course_id).all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'deadline': t.deadline.isoformat() if t.deadline else None,
        'course_id': t.course_id
    } for t in tasks])

@bp.route('/tasks', methods=['POST'])
@token_required
def create_task(current_user):
    try:
        data = request.get_json()
        task = Task(
            title=data['title'],
            description=data['description'],
            course_id=data['course_id'],
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({
            'message': 'Task created successfully',
            'id': task.id
        }), 201
    except KeyError as e:
        return jsonify({'message': f'Missing required field: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'message': f'Invalid data format: {str(e)}'}), 400

@bp.route('/tasks/<int:task_id>', methods=['GET'])
@token_required
def get_task(current_user, task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'deadline': task.deadline.isoformat() if task.deadline else None,
        'course_id': task.course_id
    })

@bp.route('/submit/<int:task_id>', methods=['POST'])
@token_required
def submit_task(current_user, task_id):
    task = Task.query.get_or_404(task_id)
    
    # Check if task deadline has passed
    if task.deadline and datetime.utcnow() > task.deadline:
        return jsonify({'message': 'Task deadline has passed'}), 400
        
    # Check if user has already submitted
    existing_submission = Submission.query.filter_by(
        task_id=task_id,
        user_id=current_user['id']
    ).first()
    
    if existing_submission:
        return jsonify({'message': 'You have already submitted this task'}), 400
    
    try:
        data = request.get_json()
        submission = Submission(
            task_id=task_id,
            user_id=current_user['id'],
            content=data['content']
        )
        db.session.add(submission)
        db.session.commit()
        return jsonify({
            'message': 'Submission received',
            'id': submission.id
        }), 201
    except KeyError:
        return jsonify({'message': 'Missing required fields'}), 400

@bp.route('/submissions/<int:task_id>', methods=['GET'])
@token_required
def get_submissions(current_user, task_id):
    # Get task to verify it exists
    task = Task.query.get_or_404(task_id)
    
    # Get all submissions for this task
    submissions = Submission.query.filter_by(task_id=task_id).all()
    return jsonify([{
        'id': s.id,
        'user_id': s.user_id,
        'content': s.content,
        'submitted_at': s.submitted_at.isoformat()
    } for s in submissions])

@bp.route('/my-submissions/<int:task_id>', methods=['GET'])
@token_required
def get_my_submissions(current_user, task_id):
    # Get user's submissions for specific task
    submissions = Submission.query.filter_by(
        task_id=task_id,
        user_id=current_user['id']
    ).all()
    
    return jsonify([{
        'id': s.id,
        'content': s.content,
        'submitted_at': s.submitted_at.isoformat()
    } for s in submissions])

@bp.route('/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(current_user, task_id):
    task = Task.query.get_or_404(task_id)
    
    try:
        data = request.get_json()
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'deadline' in data:
            task.deadline = datetime.fromisoformat(data['deadline']) if data['deadline'] else None
            
        db.session.commit()
        return jsonify({'message': 'Task updated successfully'})
    except ValueError as e:
        return jsonify({'message': f'Invalid data format: {str(e)}'}), 400

@bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user, task_id):
    task = Task.query.get_or_404(task_id)
    
    # Here you might want to add additional checks
    # For example, only allowing course instructors to delete tasks
    
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'})