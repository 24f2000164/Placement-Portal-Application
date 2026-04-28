from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.utils.decorators import role_required
from app.services import company_service

company_bp = Blueprint('company', __name__)


@company_bp.route('/dashboard', methods=['GET'])
@role_required('company')
def dashboard():
    user_id = get_jwt_identity()
    stats = company_service.get_dashboard_stats(user_id)
    if not stats:
        return jsonify({'message': 'Company not found'}), 404
    return jsonify(stats), 200


@company_bp.route('/profile', methods=['GET'])
@role_required('company')
def get_profile():
    user_id = get_jwt_identity()
    company = company_service.get_company_by_user_id(user_id)
    if not company:
        return jsonify({'message': 'Company not found'}), 404
    return jsonify(company.to_dict()), 200


@company_bp.route('/profile', methods=['PUT'])
@role_required('company')
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    company, error = company_service.update_company_profile(user_id, data)
    if error:
        return jsonify({'message': error}), 400

    return jsonify({'message': 'Profile updated successfully', 'company': company.to_dict()}), 200


@company_bp.route('/drives', methods=['GET'])
@role_required('company')
def get_drives():
    user_id = get_jwt_identity()
    drives = company_service.get_company_drives(user_id)
    return jsonify(drives), 200


@company_bp.route('/drives', methods=['POST'])
@role_required('company')
def create_drive():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    if not data.get('job_title'):
        return jsonify({'message': 'Job title is required'}), 400

    drive, error = company_service.create_drive(user_id, data)
    if error:
        return jsonify({'message': error}), 400

    return jsonify({'message': 'Drive created successfully. Awaiting admin approval.', 'drive': drive.to_dict()}), 201


@company_bp.route('/drives/<int:drive_id>', methods=['PUT'])
@role_required('company')
def update_drive(drive_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    drive, error = company_service.update_drive(user_id, drive_id, data)
    if error:
        return jsonify({'message': error}), 400

    return jsonify({'message': 'Drive updated successfully', 'drive': drive.to_dict()}), 200


@company_bp.route('/drives/<int:drive_id>/close', methods=['PUT'])
@role_required('company')
def close_drive(drive_id):
    user_id = get_jwt_identity()
    drive, error = company_service.close_drive(user_id, drive_id)
    if error:
        return jsonify({'message': error}), 400

    return jsonify({'message': 'Drive closed successfully'}), 200


@company_bp.route('/drives/<int:drive_id>/applicants', methods=['GET'])
@role_required('company')
def get_applicants(drive_id):
    user_id = get_jwt_identity()
    applicants, error = company_service.get_drive_applicants(user_id, drive_id)
    if error:
        return jsonify({'message': error}), 400

    return jsonify(applicants), 200



@company_bp.route('/applications/<int:application_id>/status', methods=['PUT'])
@role_required('company')
def update_status(application_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    status   = data.get('status')
    feedback = data.get('feedback')

    if not status and not feedback:
        return jsonify({'message': 'Status or feedback is required'}), 400

    application, error = company_service.update_application_status(
        user_id, application_id, status, feedback
    )
    if error:
        return jsonify({'message': error}), 400

    return jsonify({'message': 'Application updated', 'application': application.to_dict()}), 200


@company_bp.route('/applications/<int:application_id>/interview', methods=['POST'])
@role_required('company')
def schedule_interview(application_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    interview, error = company_service.schedule_interview(user_id, application_id, data)
    if error:
        return jsonify({'message': error}), 400

    return jsonify({'message': 'Interview scheduled successfully', 'interview': interview.to_dict()}), 201


@company_bp.route('/students/<int:student_id>', methods=['GET'])
@role_required('company')
def get_student_profile(student_id):
    user_id = get_jwt_identity()
    student, error = company_service.get_student_profile_for_company(user_id, student_id)
    if error:
        return jsonify({'message': error}), 404
    return jsonify(student), 200


@company_bp.route('/applications', methods=['GET'])
@role_required('company')
def get_all_applications():
    user_id = get_jwt_identity()
    applications = company_service.get_company_all_applications(user_id)
    return jsonify(applications), 200


@company_bp.route('/export/csv', methods=['POST'])
@role_required('company')
def trigger_csv_export():
    user_id = get_jwt_identity()
    try:
        from app.tasks.export_csv import export_company_applications
        task = export_company_applications.delay(user_id)
        return jsonify({
            'message': 'Export started. You will get an email when ready.',
            'task_id': task.id
        }), 202
    except Exception as e:
        return jsonify({'message': 'Export service unavailable. Start Celery first.'}), 503




@company_bp.route('/ping')
def ping():
    return jsonify({'message': 'company route working'}), 200