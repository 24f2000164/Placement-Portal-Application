from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import register_student, register_company, login_user, get_user_profile
from app.utils.validators import validate_registration

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register/student', methods=['POST'])
def student_register():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    errors = validate_registration(data, 'student')
    if errors:
        return jsonify({'message': errors[0]}), 400

    user, error = register_student(data)
    if error:
        return jsonify({'message': error}), 409

    return jsonify({'message': 'Student registered successfully'}), 201


@auth_bp.route('/register/company', methods=['POST'])
def company_register():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    errors = validate_registration(data, 'company')
    if errors:
        return jsonify({'message': errors[0]}), 400

    user, error = register_company(data)
    if error:
        return jsonify({'message': error}), 409

    return jsonify({'message': 'Company registered successfully. Awaiting admin approval.'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user, token, error = login_user(email, password)
    if error:
        return jsonify({'message': error}), 401

    return jsonify({
        'token': token,
        'role': user.role,
        'user_id': user.id,
        'email': user.email,
        'message': 'Login successful'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    profile = get_user_profile(user_id)
    if not profile:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(profile), 200


@auth_bp.route('/ping')
def ping():
    return jsonify({'message': 'auth route working'}), 200