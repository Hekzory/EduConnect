from flask import Blueprint, request, jsonify
from .models import Course, db
from .auth import token_required

bp = Blueprint('courses', __name__)

@bp.route('/courses', methods=['GET'])
@token_required
def get_courses(current_user):
    courses = Course.query.all()
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'description': c.description,
        'instructor_id': c.instructor_id
    } for c in courses])

@bp.route('/courses', methods=['POST'])
@token_required
def create_course(current_user):
    data = request.get_json()
    course = Course(
        title=data['title'],
        description=data['description'],
        instructor_id=current_user['id']  # Use authenticated user's ID
    )
    db.session.add(course)
    db.session.commit()
    return jsonify({'message': 'Course created successfully', 'id': course.id}), 201

@bp.route('/courses/<int:course_id>', methods=['GET'])
@token_required
def get_course(current_user, course_id):
    course = Course.query.get_or_404(course_id)
    return jsonify({
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'instructor_id': course.instructor_id
    })