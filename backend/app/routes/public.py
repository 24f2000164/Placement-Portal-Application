from flask import Blueprint, jsonify, request
from app.models.drive import PlacementDrive
from app.models.application import Application
from app.models.company import Company
from app.models.student import Student
from app.models.report import Report
from app.utils.cache import cache_get, cache_set

public_bp = Blueprint('public', __name__)


@public_bp.route('/stats', methods=['GET'])
def get_public_stats():
    cached = cache_get('public:stats')
    if cached:
        return jsonify(cached), 200

    total_companies   = Company.query.filter_by(approval_status='approved').count()
    total_drives      = PlacementDrive.query.filter_by(status='approved').count()
    total_students    = Student.query.count()
    total_selected    = Application.query.filter_by(status='selected').count()
    total_placed      = Application.query.filter_by(status='placed').count()

    stats = {
        'total_companies':  total_companies,
        'total_drives':     total_drives,
        'total_students':   total_students,
        'total_selected':   total_selected,
        'total_placed':     total_placed
    }

    cache_set('public:stats', stats, 300)
    return jsonify(stats), 200


@public_bp.route('/monthly-trends', methods=['GET'])
def get_monthly_trends():
    cached = cache_get('public:monthly:trends')
    if cached:
        return jsonify(cached), 200

    reports = Report.query.order_by(Report.year, Report.month).limit(12).all()
    data = []
    for r in reports:
        from datetime import datetime
        month_name = datetime(r.year, r.month, 1).strftime('%b %Y')
        data.append({
            'month':        month_name,
            'drives':       r.total_drives,
            'applications': r.total_applications,
            'selected':     r.total_selected
        })

    cache_set('public:monthly:trends', data, 300)
    return jsonify(data), 200


@public_bp.route('/seed-admin-once', methods=['GET'])
def seed_admin():
    secret = request.args.get('secret', '')
    if secret != 'ppa-init-2026':
        return jsonify({'message': 'Unauthorized'}), 401

    from app.extensions import db
    from app.models.user import User

    existing = User.query.filter_by(role='admin').first()
    if existing:
        return jsonify({'message': f'Admin already exists: {existing.email}'}), 200

    admin = User(
        email='bt23ece015@nituk.ac.in',
        role='admin',
        is_active=True,
        is_blacklisted=False
    )
    admin.set_password('Admin@123')
    db.session.add(admin)
    db.session.commit()

    return jsonify({'message': 'Admin created!', 'email': 'bt23ece015@nituk.ac.in'}), 201


@public_bp.route('/reset-admin-pass', methods=['GET'])
def reset_admin():
    secret = request.args.get('secret', '')
    if secret != 'ppa-reset-2026':
        return jsonify({'message': 'Unauthorized'}), 401

    from app.extensions import db
    from app.models.user import User

    admin = User.query.filter_by(role='admin').first()
    if not admin:
        return jsonify({'message': 'No admin found'}), 404

    admin.set_password('Admin@123')
    db.session.commit()

    return jsonify({'message': 'Password reset to Admin@123'}), 200