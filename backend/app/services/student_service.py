from app.extensions import db
from app.models.student import Student
from app.models.drive import PlacementDrive
from app.models.application import Application
from app.models.user import User
import os
from werkzeug.utils import secure_filename


from app.utils.cache import cache_get, cache_set, cache_clear_prefix, LIST_EXPIRY, SEARCH_EXPIRY,cache_delete


def get_student_by_user_id(user_id):
    return Student.query.filter_by(user_id=user_id).first()


def update_student_profile(user_id, data):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return None, 'Student not found'

    student.full_name = data.get('full_name', student.full_name)
    student.phone     = data.get('phone', student.phone)
    student.branch    = data.get('branch', student.branch)
    student.cgpa      = data.get('cgpa', student.cgpa)
    student.year      = data.get('year', student.year)
    student.skills    = data.get('skills', student.skills)
    student.experience  = data.get('experience', student.experience) 
    student.linkdin_url = data.get('linkdin_url',student.linkdin_url)

    db.session.commit()
    # After db.session.commit(), ADD:
    cache_clear_prefix('admin:students')
    cache_clear_prefix('admin:search:students')
    return student, None


def save_resume(user_id, file, upload_folder):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return None, 'Student not found'
    os.makedirs(upload_folder, exist_ok=True)

    filename = secure_filename('resume_' + str(user_id) + '_' + file.filename)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    student.resume_path = filename
    db.session.commit()
    return student, None


def get_approved_drives(search=None, branch=None, min_cgpa=None):
    cache_key = 'student:drives:approved'
    if search:
        cache_key += ':search:' + search.lower()
    if branch:
        cache_key += ':branch:' + branch.upper()
    if min_cgpa:
        cache_key += ':cgpa:' + str(min_cgpa)

    cached = cache_get(cache_key)
    if cached:
        return cached

    query = PlacementDrive.query.filter_by(status='approved')

    if search:
        query = query.filter(
            PlacementDrive.job_title.ilike('%' + search + '%') |
            PlacementDrive.skills_required.ilike('%' + search + '%') |
            PlacementDrive.location.ilike('%' + search + '%')
        )

    drives = query.all()

    if branch:
        drives = [
            d for d in drives
            if not d.eligible_branches or
            branch.upper() in [b.strip().upper() for b in d.eligible_branches.split(',')]
        ]

    if min_cgpa is not None and min_cgpa != '':
        try:
             drives = [d for d in drives if d.min_cgpa is None or d.min_cgpa <= float(min_cgpa)]
        except Exception:
             pass

    result = [d.to_dict() for d in drives]
    cache_set(cache_key, result, LIST_EXPIRY)
    return result

  


def check_eligibility(student, drive):
    errors = []

    if drive.min_cgpa and student.cgpa is not None:
        if student.cgpa < drive.min_cgpa:
            errors.append(
                'Your CGPA ' + str(student.cgpa) +
                ' is below the required ' + str(drive.min_cgpa)
            )

    if drive.eligible_branches and student.branch:
        allowed = [b.strip().upper() for b in drive.eligible_branches.split(',')]
        if student.branch.upper() not in allowed:
            errors.append(
                'Your branch ' + student.branch +
                ' is not eligible. Allowed: ' + drive.eligible_branches
            )

    if drive.eligible_year and student.year:
        if int(student.year) != int(drive.eligible_year):
            errors.append(
                'This drive is only for year ' +
                str(drive.eligible_year) + ' students'
            )

    return errors


def apply_to_drive(user_id, drive_id):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return None, 'Student profile not found. Please complete your profile first.'

    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return None, 'Drive not found'

    if drive.status != 'approved':
        return None, 'This drive is not open for applications'

    existing = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive_id
    ).first()
    if existing:
        return None, 'You have already applied to this drive'

    eligibility_errors = check_eligibility(student, drive)
    if eligibility_errors:
        return None, eligibility_errors[0]

    application = Application(
        student_id=student.id,
        drive_id=drive_id,
        status='applied'
    )
    db.session.add(application)
    db.session.commit()

    cache_clear_prefix('student:applications:' + str(user_id))
    cache_clear_prefix('student:drives')
    cache_delete('admin:dashboard:stats')
    cache_delete('admin:applications:all')

    return application, None


def get_my_applications(user_id):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return []

    cache_key = 'student:applications:' + str(user_id)
    cached = cache_get(cache_key)
    if cached:
        return cached

    applications = Application.query.filter_by(
        student_id=student.id
    ).order_by(Application.applied_at.desc()).all()

    result = []
    for app in applications:
        data = app.to_dict()
        data['interview'] = app.interview.to_dict() if app.interview else None
        data['feedback'] = app.feedback if hasattr(app, 'feedback') else None
        result.append(data)

    cache_set(cache_key, result, LIST_EXPIRY)
    return result


def get_placement_history(user_id):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return []

    applications = Application.query.filter_by(
        student_id=student.id
    ).order_by(Application.applied_at.desc()).all()

    history = []
    for app in applications:
        entry = {
            'application_id':   app.id,
            'student_id':       student.id,
            'drive_id':         app.drive_id,
            'drive_title':      app.drive.job_title if app.drive else None,
            'company_name':     app.drive.company.company_name if app.drive and app.drive.company else None,
            'applied_at':       app.applied_at.isoformat(),
            'updated_at':       app.updated_at.isoformat(),
            'status':           app.status,
            'salary':           app.drive.salary if app.drive else None,
            'location':         app.drive.location if app.drive else None,
            'interview_mode':   app.interview.mode if app.interview else None,
            'interview_result': app.interview.result if app.interview else None,
            'interview_date':   app.interview.scheduled_at.isoformat() if app.interview and app.interview.scheduled_at else None,
            'interview_venue':  app.interview.venue if app.interview else None
        }
        history.append(entry)

    return history


def get_application_status_timeline(user_id, application_id):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return None, 'Student not found'

    application = Application.query.filter_by(
        id=application_id,
        student_id=student.id
    ).first()

    if not application:
        return None, 'Application not found or access denied'

    all_statuses = ['applied', 'shortlisted', 'interview', 'offer', 'selected', 'placed', 'rejected']
    current_index = all_statuses.index(application.status) if application.status in all_statuses else 0

    timeline = {
        'application_id': application.id,
        'drive_title':    application.drive.job_title if application.drive else None,
        'company_name':   application.drive.company.company_name if application.drive and application.drive.company else None,
        'current_status': application.status,
        'applied_at':     application.applied_at.isoformat(),
        'updated_at':     application.updated_at.isoformat(),
        'interview':      application.interview.to_dict() if application.interview else None,
        'all_statuses':   all_statuses,
        'current_index':  current_index
    }

    return timeline, None