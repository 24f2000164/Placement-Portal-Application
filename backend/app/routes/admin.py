from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.utils.decorators import role_required
from app.services import admin_service

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard', methods=['GET'])
@role_required('admin')
def dashboard():
    stats = admin_service.get_dashboard_stats()
    return jsonify(stats), 200


@admin_bp.route('/companies', methods=['GET'])
@role_required('admin')
def get_companies():
    companies = admin_service.get_all_companies()
    return jsonify(companies), 200


@admin_bp.route('/students', methods=['GET'])
@role_required('admin')
def get_students():
    students = admin_service.get_all_students()
    return jsonify(students), 200


@admin_bp.route('/drives', methods=['GET'])
@role_required('admin')
def get_drives():
    drives = admin_service.get_all_drives()
    return jsonify(drives), 200


@admin_bp.route('/applications', methods=['GET'])
@role_required('admin')
def get_applications():
    applications = admin_service.get_all_applications()
    return jsonify(applications), 200


@admin_bp.route('/companies/<int:company_id>/approve', methods=['PUT'])
@role_required('admin')
def approve_company(company_id):
    admin_id = get_jwt_identity()
    company, error = admin_service.approve_company(company_id, admin_id)
    if error:
        return jsonify({'message': error}), 404
    return jsonify({'message': 'Company approved successfully'}), 200


@admin_bp.route('/companies/<int:company_id>/reject', methods=['PUT'])
@role_required('admin')
def reject_company(company_id):
    admin_id = get_jwt_identity()
    company, error = admin_service.reject_company(company_id, admin_id)
    if error:
        return jsonify({'message': error}), 404
    return jsonify({'message': 'Company rejected'}), 200


@admin_bp.route('/companies/<int:company_id>/blacklist', methods=['PUT'])
@role_required('admin')
def blacklist_company(company_id):
    admin_id = get_jwt_identity()
    company, error = admin_service.blacklist_company(company_id, admin_id)
    if error:
        return jsonify({'message': error}), 404
    return jsonify({'message': 'Company blacklisted and all drives closed'}), 200


@admin_bp.route('/companies/<int:company_id>/unblacklist', methods=['PUT'])
@role_required('admin')
def unblacklist_company(company_id):
    admin_id = get_jwt_identity()
    company, error = admin_service.unblacklist_company(company_id, admin_id)
    if error:
        return jsonify({'message': error}), 404
    return jsonify({'message': 'Company unblacklisted successfully'}), 200


@admin_bp.route('/students/<int:student_id>/blacklist', methods=['PUT'])
@role_required('admin')
def blacklist_student(student_id):
    admin_id = get_jwt_identity()
    student, error = admin_service.blacklist_student(student_id, admin_id)
    if error:
        return jsonify({'message': error}), 404
    return jsonify({'message': 'Student blacklisted'}), 200


@admin_bp.route('/students/<int:student_id>/unblacklist', methods=['PUT'])
@role_required('admin')
def unblacklist_student(student_id):
    admin_id = get_jwt_identity()
    student, error = admin_service.unblacklist_student(student_id, admin_id)
    if error:
        return jsonify({'message': error}), 404
    return jsonify({'message': 'Student unblacklisted'}), 200


@admin_bp.route('/drives/<int:drive_id>/approve', methods=['PUT'])
@role_required('admin')
def approve_drive(drive_id):
    admin_id = get_jwt_identity()
    drive, error = admin_service.approve_drive(drive_id, admin_id)
    if error:
        return jsonify({'message': error}), 404
    return jsonify({'message': 'Drive approved successfully'}), 200


@admin_bp.route('/drives/<int:drive_id>/reject', methods=['PUT'])
@role_required('admin')
def reject_drive(drive_id):
    admin_id = get_jwt_identity()
    drive, error = admin_service.reject_drive(drive_id, admin_id)
    if error:
        return jsonify({'message': error}), 404
    return jsonify({'message': 'Drive rejected'}), 200


 
@admin_bp.route('/search/companies', methods=['GET'])
@role_required('admin')
def search_companies():
    query    = request.args.get('q', '')
    name     = request.args.get('name', '')
    industry = request.args.get('industry', '')
    
    # combine into one search term if separate fields used
    search_term = query or name or industry
    if not search_term and not industry:
        return jsonify([]), 200
    
    results = admin_service.search_companies_advanced(search_term, name, industry)
    return jsonify(results), 200

@admin_bp.route('/search/students', methods=['GET'])
@role_required('admin')
def search_students():
    query = request.args.get('q', '')
    if not query:
        return jsonify([]), 200
    results = admin_service.search_students(query)
    return jsonify(results), 200


@admin_bp.route('/logs', methods=['GET'])
@role_required('admin')
def get_logs():
    logs = admin_service.get_admin_logs()
    return jsonify(logs), 200


@admin_bp.route('/students/<int:student_id>', methods=['GET'])
@role_required('admin')
def get_student_profile(student_id):
    from app.models.student import Student
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'message': 'Student not found'}), 404

    data = student.to_dict()
    applications = student.applications.all()
    data['applications'] = [a.to_dict() for a in applications]
    return jsonify(data), 200


@admin_bp.route('/companies/<int:company_id>', methods=['GET'])
@role_required('admin')
def get_company_detail(company_id):
    from app.models.company import Company
    company = Company.query.get(company_id)
    if not company:
        return jsonify({'message': 'Company not found'}), 404

    data = company.to_dict()
    drives = company.drives.all()
    data['drives'] = [d.to_dict() for d in drives]
    return jsonify(data), 200



@admin_bp.route('/reports', methods=['GET'])
@role_required('admin')
def get_reports():
    from app.models.report import Report
    reports = Report.query.order_by(Report.year.desc(), Report.month.desc()).all()
    return jsonify([r.to_dict() for r in reports]), 200


@admin_bp.route('/reports/generate', methods=['POST'])
@role_required('admin')
def trigger_report():
    from app.tasks.monthly_report import generate_monthly_report
    try:
        task = generate_monthly_report.delay()
        return jsonify({
            'message': 'Report generation started',
            'task_id': task.id
        }), 202
    except Exception as e:
        return jsonify({'message': 'Celery not running. Start celery worker first.'}), 503


@admin_bp.route('/reports/download/<filename>', methods=['GET'])
@role_required('admin')
def download_report(filename):
    import os
    from flask import send_from_directory, current_app
    reports_dir = current_app.config['REPORTS_FOLDER']
    return send_from_directory(reports_dir, filename)

@admin_bp.route('/cache/stats', methods=['GET'])
@role_required('admin')
def cache_stats():
    from app.extensions import redis_client
    try:
        info = redis_client.info('memory')
        keys = redis_client.keys('*')
        ppa_keys = [k for k in keys if any(prefix in k for prefix in ['admin:', 'student:', 'company:'])]

        return jsonify({
            'total_redis_keys': len(keys),
            'ppa_cache_keys':   len(ppa_keys),
            'ppa_keys_list':    ppa_keys,
            'redis_memory_used': info.get('used_memory_human', 'N/A'),
            'status': 'Redis connected'
        }), 200
    except Exception as e:
        return jsonify({'message': 'Redis error: ' + str(e)}), 500


@admin_bp.route('/cache/clear', methods=['POST'])
@role_required('admin')
def clear_cache():
    from app.utils.cache import cache_clear_prefix
    cache_clear_prefix('admin:')
    cache_clear_prefix('student:')
    cache_clear_prefix('company:')
    return jsonify({'message': 'All PPA cache cleared successfully'}), 200


@admin_bp.route('/ping')
def ping():
    return jsonify({'message': 'admin route working'}), 200


 