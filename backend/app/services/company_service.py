from app.extensions import db
from app.models.company import Company
from app.models.drive import PlacementDrive
from app.models.application import Application
from app.models.interview import Interview
from app.models.student import Student



from app.utils.cache import cache_get, cache_set, cache_delete, cache_clear_prefix, DASHBOARD_EXPIRY, LIST_EXPIRY


def get_company_by_user_id(user_id):
    return Company.query.filter_by(user_id=user_id).first()


def update_company_profile(user_id, data):
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return None, 'Company not found'

    company.company_name = data.get('company_name', company.company_name)
    company.industry = data.get('industry', company.industry)
    company.location = data.get('location', company.location)
    company.website = data.get('website', company.website)
    company.hr_contact = data.get('hr_contact', company.hr_contact)
    company.hr_phone = data.get('hr_phone', company.hr_phone)
    company.description = data.get('description', company.description)
    

    db.session.commit()
    cache_clear_prefix('company:drives:' + str(user_id))
     
    cache_delete('company:dashboard:' + str(user_id))
    cache_clear_prefix('admin:companies')
    cache_clear_prefix('admin:search:companies')
    return company, None


def get_company_drives(user_id):
    cache_key = 'company:drives:' + str(user_id)
    cached = cache_get(cache_key)
    if cached:
        return cached

    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return []

    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    result = []
    for drive in drives:
        data = drive.to_dict()
        data['applicant_count'] = drive.applications.count()
        result.append(data)

    cache_set(cache_key, result, LIST_EXPIRY)
    return result

def create_drive(user_id, data):
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return None, 'Company not found'

    if company.approval_status != 'approved':
        return None, 'Your company is not approved yet. Please wait for admin approval.'

    from datetime import datetime

    deadline = None
    if data.get('application_deadline'):
        try:
            deadline = datetime.fromisoformat(data['application_deadline'])
        except Exception:
            return None, 'Invalid deadline format. Use YYYY-MM-DD'

    drive = PlacementDrive(
        company_id=company.id,
        job_title=data.get('job_title', ''),
        job_description=data.get('job_description', ''),
        eligible_branches=data.get('eligible_branches', ''),
        min_cgpa=data.get('min_cgpa', 0.0),
        eligible_year=data.get('eligible_year', None),
        salary=data.get('salary', ''),
        location=data.get('location', ''),
        skills_required=data.get('skills_required', ''),
        application_deadline=deadline,
        status='pending'
    )

    db.session.add(drive)
    db.session.commit()

    cache_clear_prefix('company:drives:' + str(user_id))
    cache_clear_prefix('company:applicants:')
    cache_delete('company:dashboard:' + str(user_id))
    cache_delete('admin:drives:all')
    cache_delete('admin:dashboard:stats')

    return drive, None

def update_drive(user_id, drive_id, data):
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return None, 'Company not found'

    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        return None, 'Drive not found'

    if drive.status == 'closed':
        return None, 'Cannot edit a closed drive'

    from datetime import datetime

    drive.job_title = data.get('job_title', drive.job_title)
    drive.job_description = data.get('job_description', drive.job_description)
    drive.eligible_branches = data.get('eligible_branches', drive.eligible_branches)
    drive.min_cgpa = data.get('min_cgpa', drive.min_cgpa)
    drive.eligible_year = data.get('eligible_year', drive.eligible_year)
    drive.salary = data.get('salary', drive.salary)
    drive.location = data.get('location', drive.location)
    drive.skills_required = data.get('skills_required', drive.skills_required)

    if data.get('application_deadline'):
        try:
            drive.application_deadline = datetime.fromisoformat(data['application_deadline'])
        except Exception:
            return None, 'Invalid deadline format'

    db.session.commit()
    # After db.session.commit() in update_drive, ADD:
    cache_clear_prefix('company:drives:' + str(user_id))
    cache_delete('company:dashboard:' + str(user_id))
    cache_clear_prefix('admin:drives')
    cache_clear_prefix('student:drives')
    return drive, None    


def close_drive(user_id, drive_id):
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return None, 'Company not found'

    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        return None, 'Drive not found'

    drive.status = 'closed'
    db.session.commit()

    cache_clear_prefix('company:drives:' + str(user_id))
    cache_delete('company:dashboard:' + str(user_id))
    cache_clear_prefix('admin:drives')
    cache_clear_prefix('student:drives')
    cache_delete('admin:dashboard:stats')

    return drive, None


def get_drive_applicants(user_id, drive_id):
    cache_key = 'company:applicants:' + str(drive_id)
    cached = cache_get(cache_key)
    if cached:
        return cached, None

    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return None, 'Company not found'

    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        return None, 'Drive not found'

    applications = Application.query.filter_by(drive_id=drive_id).all()
    result = []

    for app in applications:
        data = app.to_dict()
        if app.student:
            data['student_details'] = app.student.to_dict()
        if app.interview:
            data['interview'] = app.interview.to_dict()
        else:
            data['interview'] = None
        result.append(data)

    cache_set(cache_key, result, LIST_EXPIRY)
    return result, None


def update_application_status(user_id, application_id, status, feedback=None):
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return None, 'Company not found'

    application = Application.query.get(application_id)
    if not application:
        return None, 'Application not found'

    drive = PlacementDrive.query.filter_by(
        id=application.drive_id,
        company_id=company.id
    ).first()
    if not drive:
        return None, 'You do not have permission to update this application'

    allowed_statuses = ['applied', 'shortlisted', 'interview', 'offer', 'selected', 'rejected', 'placed']

    if status:
        if status not in allowed_statuses:
            return None, 'Invalid status value'
        application.status = status

    if feedback:
        application.feedback = feedback

    db.session.commit()

    cache_clear_prefix('student:applications:' + str(application.student.user_id))
    cache_delete('company:dashboard:' + str(user_id))
    cache_delete('admin:applications:all')
    cache_delete('admin:dashboard:stats')

    return application, None


def schedule_interview(user_id, application_id, data):
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return None, 'Company not found'

    application = Application.query.get(application_id)
    if not application:
        return None, 'Application not found'

    drive = PlacementDrive.query.filter_by(
        id=application.drive_id,
        company_id=company.id
    ).first()
    if not drive:
        return None, 'You do not have permission for this application'

    from datetime import datetime

    scheduled_at = None
    if data.get('scheduled_at'):
        try:
            scheduled_at = datetime.fromisoformat(data['scheduled_at'])
        except Exception:
            return None, 'Invalid date format. Use YYYY-MM-DDTHH:MM'

    existing = Interview.query.filter_by(application_id=application_id).first()

    if existing:
        existing.scheduled_at = scheduled_at
        existing.mode = data.get('mode', existing.mode)
        existing.venue = data.get('venue', existing.venue)
        existing.notes = data.get('notes', existing.notes)
        existing.result = data.get('result', existing.result)

         
        if existing.result == 'passed':
            existing.application.status = 'selected'
        elif existing.result == 'failed':
            existing.application.status = 'rejected'
        

        db.session.commit()
        cache_delete('company:applicants:' + str(application.drive_id))

        cache_clear_prefix('student:applications:' + str(application.student.user_id))
        cache_delete('company:dashboard:' + str(user_id))
        cache_delete('admin:applications:all')
        return existing, None
    

    interview = Interview(
        application_id=application_id,
        scheduled_at=scheduled_at,
        mode=data.get('mode', 'In-person'),
        venue=data.get('venue', ''),
        notes=data.get('notes', ''),
        result=data.get('result', 'pending')
    )
    db.session.add(interview)

    
    result = data.get('result', 'pending')
    if result == 'passed':
        application.status = 'selected'
    elif result == 'failed':
        application.status = 'rejected'
    else:
        application.status = 'interview'

    db.session.commit()
    cache_delete('company:applicants:' + str(application.drive_id))
    cache_clear_prefix('student:applications:' + str(application.student.user_id))
    cache_delete('company:dashboard:' + str(user_id))
    return interview, None


def get_dashboard_stats(user_id):
    cache_key = 'company:dashboard:' + str(user_id)
    cached = cache_get(cache_key)
    if cached:
        return cached

    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return None

   
  
    approved_drives = PlacementDrive.query.filter_by(company_id=company.id, status='approved').count()
    pending_drives  = PlacementDrive.query.filter_by(company_id=company.id, status='pending').count()
    closed_drives   = PlacementDrive.query.filter_by(company_id=company.id, status='closed').count()
    rejected_drives = PlacementDrive.query.filter_by(company_id=company.id, status='rejected').count()
 
    total_drives    = approved_drives + pending_drives + closed_drives + rejected_drives

    drive_ids = [d.id for d in PlacementDrive.query.filter_by(company_id=company.id).all()]

    total_applicants  = 0
    total_selected    = 0
    total_shortlisted = 0

    if drive_ids:
        total_applicants  = Application.query.filter(Application.drive_id.in_(drive_ids)).count()
        total_selected    = Application.query.filter(Application.drive_id.in_(drive_ids), Application.status == 'selected').count()
        total_shortlisted = Application.query.filter(Application.drive_id.in_(drive_ids), Application.status == 'shortlisted').count()

    stats = {
        'company_name':    company.company_name,
        'approval_status': company.approval_status,
        'total_drives':    total_drives,
        'approved_drives': approved_drives,
        'pending_drives':  pending_drives,
        'closed_drives':   closed_drives,
        'rejected_drives': rejected_drives, 
        'total_applicants':  total_applicants,
        'total_selected':    total_selected,
        'total_shortlisted': total_shortlisted
    }

    cache_set(cache_key, stats, DASHBOARD_EXPIRY)
    return stats