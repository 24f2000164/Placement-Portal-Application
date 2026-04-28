from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User


def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception:
                return jsonify({'message': 'Missing or invalid token'}), 401

            user_id = get_jwt_identity()
            # user = User.query.get(user_id)
            user = User.query.get(int(user_id))  

            if not user:
                return jsonify({'message': 'User not found'}), 404

            if user.is_blacklisted:
                return jsonify({'message': 'Your account has been blacklisted. Contact admin.'}), 403

            if not user.is_active:
                return jsonify({'message': 'Your account is deactivated. Contact admin.'}), 403

            if user.role not in roles:
                return jsonify({'message': 'Access denied. Insufficient permissions.'}), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper


def login_required(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({'message': 'Missing or invalid token'}), 401

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'message': 'User not found'}), 404

        if not user.is_active:
            return jsonify({'message': 'Your account is deactivated'}), 403

        if user.is_blacklisted:
            return jsonify({'message': 'Your account has been blacklisted'}), 403

        return fn(*args, **kwargs)
    return decorator


def company_approved_required(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({'message': 'Missing or invalid token'}), 401

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role != 'company':
            return jsonify({'message': 'Access denied'}), 403

        from app.models.company import Company
        company = Company.query.filter_by(user_id=user_id).first()

        if not company:
            return jsonify({'message': 'Company profile not found'}), 404

        if company.approval_status != 'approved':
            return jsonify({'message': 'Your company is not approved yet. Please wait for admin approval.'}), 403

        return fn(*args, **kwargs)
    return decorator