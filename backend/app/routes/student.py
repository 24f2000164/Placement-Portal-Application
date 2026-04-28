from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from app.utils.decorators import role_required
from app.services import student_service
from app.extensions import db

student_bp = Blueprint('student', __name__)


@student_bp.route('/profile', methods=['GET'])
@role_required('student')
def get_profile():
    user_id = get_jwt_identity()
    student = student_service.get_student_by_user_id(user_id)
    if not student:
        return jsonify({'message': 'Profile not found'}), 404
    return jsonify(student.to_dict()), 200


@student_bp.route('/profile', methods=['PUT'])
@role_required('student')
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    student, error = student_service.update_student_profile(user_id, data)
    if error:
        return jsonify({'message': error}), 404

    return jsonify({'message': 'Profile updated successfully', 'student': student.to_dict()}), 200



@student_bp.route('/resume', methods=['POST'])
@role_required('student')
def upload_resume():
    user_id = get_jwt_identity()

    if 'resume' not in request.files:
        return jsonify({'message': 'No file provided'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    allowed = {'pdf', 'doc', 'docx'}
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed:
        return jsonify({'message': 'Only PDF, DOC, DOCX files allowed'}), 400

    
    try:
        student, error = student_service.save_resume(
            user_id,
            file,
            current_app.config['UPLOAD_FOLDER']
        )
        if error:
            return jsonify({'message': error}), 404
    except Exception as e:
        current_app.logger.error(f"Resume upload error: {e}")
        return jsonify({'message': 'File could not be saved. Check server permissions.'}), 500

    return jsonify({'message': 'Resume uploaded successfully'}), 200


# 
@student_bp.route('/drives', methods=['GET'])
@role_required('student')
def get_drives():
    search   = request.args.get('search', None)
    branch   = request.args.get('branch', None)
    min_cgpa = request.args.get('min_cgpa', None)

    drives = student_service.get_approved_drives(search, branch, min_cgpa)
    return jsonify(drives), 200


@student_bp.route('/drives/<int:drive_id>', methods=['GET'])
@role_required('student')
def get_drive_detail(drive_id):
    from app.models.drive import PlacementDrive
    drive = PlacementDrive.query.get(drive_id)
    if not drive or drive.status != 'approved':
        return jsonify({'message': 'Drive not found'}), 404
    return jsonify(drive.to_dict()), 200


@student_bp.route('/apply/<int:drive_id>', methods=['POST'])
@role_required('student')
def apply(drive_id):
    user_id = get_jwt_identity()
    application, error = student_service.apply_to_drive(user_id, drive_id)
    if error:
        return jsonify({'message': error}), 400
    return jsonify({
        'message': 'Applied successfully',
        'application': application.to_dict()
    }), 201


@student_bp.route('/applications', methods=['GET'])
@role_required('student')
def get_applications():
    user_id = get_jwt_identity()
    applications = student_service.get_my_applications(user_id)
    return jsonify(applications), 200


@student_bp.route('/applications/<int:application_id>/timeline', methods=['GET'])
@role_required('student')
def get_timeline(application_id):
    user_id = get_jwt_identity()
    timeline, error = student_service.get_application_status_timeline(user_id, application_id)
    if error:
        return jsonify({'message': error}), 404
    return jsonify(timeline), 200


@student_bp.route('/history', methods=['GET'])
@role_required('student')
def get_history():
    user_id = get_jwt_identity()
    history = student_service.get_placement_history(user_id)
    return jsonify(history), 200









@student_bp.route('/export/csv', methods=['POST'])
@role_required('student')
def trigger_csv_export():
    user_id = get_jwt_identity()
    try:
        from app.tasks.export_csv import export_student_applications
        task = export_student_applications.delay(user_id)
        return jsonify({
            'message': 'Export started. You will get a notification when ready.',
            'task_id': task.id
        }), 202
    except Exception as e:
        print('Export error:', str(e))
        return jsonify({'message': 'Export service unavailable. Make sure Celery is running.'}), 503





@student_bp.route('/cache/clear', methods=['POST'])
@role_required('student')
def clear_my_cache():
    user_id = get_jwt_identity()
    from app.utils.cache import cache_clear_prefix
    cache_clear_prefix('student:applications:' + str(user_id))
    return jsonify({'message': 'Your cache cleared'}), 200


@student_bp.route('/applications/<int:application_id>/confirmation', methods=['GET'])
@role_required('student')
def download_confirmation(application_id):
    user_id = get_jwt_identity()
    from app.models.student import Student
    from app.models.application import Application
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'message': 'Student not found'}), 404

    app = Application.query.filter_by(
        id=application_id,
        student_id=student.id
    ).first()
    if not app:
        return jsonify({'message': 'Application not found'}), 404

    if app.status not in ['selected', 'placed']:
        return jsonify({'message': 'Confirmation only available for selected candidates'}), 403

    # Generate simple HTML confirmation
    html = f"""
    <html><body style="font-family:Arial;padding:40px;">
    <h2>Placement Confirmation</h2>
    <hr/>
    <p><strong>Student Name:</strong> {student.full_name}</p>
    <p><strong>Company:</strong> {app.drive.company.company_name if app.drive and app.drive.company else 'N/A'}</p>
    <p><strong>Position:</strong> {app.drive.job_title if app.drive else 'N/A'}</p>
    <p><strong>Salary:</strong> {app.drive.salary if app.drive else 'N/A'}</p>
    <p><strong>Status:</strong> {app.status.upper()}</p>
    <p><strong>Date:</strong> {app.updated_at.strftime('%d %B %Y')}</p>
    <hr/>
    <p style="color:green;font-size:18px;"><strong>Congratulations!</strong></p>
    <p style="color:#999;font-size:12px;">Generated by Placement Portal</p>
    </body></html>
    """
    from flask import Response
    return Response(
        html,
        mimetype='text/html',
        headers={'Content-Disposition': f'attachment;filename=confirmation_{application_id}.html'}
    )




@student_bp.route('/ping')
def ping():
    return jsonify({'message': 'student route working'}), 200
