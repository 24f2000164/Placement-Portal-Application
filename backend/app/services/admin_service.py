from app.extensions import db
from app.models.user import User
from app.models.student import Student
from app.models.company import Company
from app.models.drive import PlacementDrive
from app.models.application import Application
from app.models.admin_log import AdminLog
from app.utils.cache import cache_get, cache_set, cache_delete, cache_clear_prefix, DASHBOARD_EXPIRY, LIST_EXPIRY, SEARCH_EXPIRY


def log_action(admin_id, action, target_type, target_id):
    log = AdminLog(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id
    )
    db.session.add(log)
    db.session.commit()
    cache_delete('admin:logs')


def get_dashboard_stats():
    cached = cache_get('admin:dashboard:stats')
    if cached:
        return cached

    total_students     = Student.query.count()
    total_companies    = Company.query.count()
    total_drives       = PlacementDrive.query.count()
    total_applications = Application.query.count()
    approved_companies = Company.query.filter_by(approval_status='approved').count()
    pending_companies  = Company.query.filter_by(approval_status='pending').count()
    approved_drives    = PlacementDrive.query.filter_by(status='approved').count()
    pending_drives     = PlacementDrive.query.filter_by(status='pending').count()
    selected_students  = Application.query.filter_by(status='selected').count()

    stats = {
        'total_students':     total_students,
        'total_companies':    total_companies,
        'total_drives':       total_drives,
        'total_applications': total_applications,
        'approved_companies': approved_companies,
        'pending_companies':  pending_companies,
        'approved_drives':    approved_drives,
        'pending_drives':     pending_drives,
        'selected_students':  selected_students
    }

    cache_set('admin:dashboard:stats', stats, DASHBOARD_EXPIRY)
    return stats


def get_all_companies():
    cached = cache_get('admin:companies:all')
    if cached:
        return cached

    companies = Company.query.all()
    result = []
    for c in companies:
        data = c.to_dict()
        data['is_blacklisted'] = c.user.is_blacklisted if c.user else False
        data['is_active']      = c.user.is_active if c.user else True
        data['drive_count']    = c.drives.count()
        result.append(data)

    cache_set('admin:companies:all', result, LIST_EXPIRY)
    return result


def get_all_students():
    cached = cache_get('admin:students:all')
    if cached:
        return cached

    students = Student.query.all()
    result = []
    for s in students:
        data = s.to_dict()
        data['is_blacklisted']    = s.user.is_blacklisted if s.user else False
        data['is_active']         = s.user.is_active if s.user else True
        data['application_count'] = s.applications.count()
        result.append(data)

    cache_set('admin:students:all', result, LIST_EXPIRY)
    return result


def get_all_drives():
    cached = cache_get('admin:drives:all')
    if cached:
        return cached

    drives = PlacementDrive.query.all()
    result = [d.to_dict() for d in drives]
    cache_set('admin:drives:all', result, LIST_EXPIRY)
    return result


def get_all_applications():
    cached = cache_get('admin:applications:all')
    if cached:
        return cached

    applications = Application.query.all()
    result = [a.to_dict() for a in applications]
    cache_set('admin:applications:all', result, LIST_EXPIRY)
    return result


def approve_company(company_id, admin_id):
    company = Company.query.get(company_id)
    if not company:
        return None, 'Company not found'
    company.approval_status = 'approved'
    db.session.commit()
    log_action(admin_id, 'approved_company', 'company', company_id)
    invalidate_company_cache()
   
    cache_delete('company:dashboard:' + str(company.user_id))
    return company, None


def reject_company(company_id, admin_id):
    company = Company.query.get(company_id)
    if not company:
        return None, 'Company not found'
    company.approval_status = 'rejected'
    db.session.commit()
    log_action(admin_id, 'rejected_company', 'company', company_id)
    invalidate_company_cache()
    
    cache_delete('company:dashboard:' + str(company.user_id))
    return company, None


def approve_drive(drive_id, admin_id):
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return None, 'Drive not found'
    company_user_id = drive.company.user_id if drive.company else None
    drive.status = 'approved'
    db.session.commit()
    log_action(admin_id, 'approved_drive', 'drive', drive_id)
    invalidate_drive_cache()
    if company_user_id:
        cache_delete('company:dashboard:' + str(company_user_id))
    return drive, None


def reject_drive(drive_id, admin_id):
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return None, 'Drive not found'
    company_user_id = drive.company.user_id if drive.company else None
    drive.status = 'rejected'
    db.session.commit()
    log_action(admin_id, 'rejected_drive', 'drive', drive_id)
    invalidate_drive_cache()
    if company_user_id:
        cache_delete('company:dashboard:' + str(company_user_id))
    return drive, None


def blacklist_company(company_id, admin_id):
    company = Company.query.get(company_id)
    if not company:
        return None, 'Company not found'
    user = User.query.get(company.user_id)
    user.is_blacklisted = True
    user.is_active = False
    drives = PlacementDrive.query.filter_by(company_id=company_id).all()
    for drive in drives:
        drive.status = 'closed'
    db.session.commit()
    cache_delete('company:dashboard:' + str(company.user_id))
    invalidate_company_cache()
    cache_clear_prefix('student:drives') 


    log_action(admin_id, 'blacklisted_company', 'company', company_id)
    invalidate_company_cache()
    invalidate_drive_cache()
    return company, None


def unblacklist_company(company_id, admin_id):
    company = Company.query.get(company_id)
    if not company:
        return None, 'Company not found'
    user = User.query.get(company.user_id)
    user.is_blacklisted = False
    user.is_active = True
    db.session.commit()
   
    cache_delete('company:dashboard:' + str(company.user_id))
    invalidate_company_cache()
    cache_clear_prefix('student:drives')  # blacklisted company drives should disappear

    log_action(admin_id, 'unblacklisted_company', 'company', company_id)
    invalidate_company_cache()
    return company, None


def blacklist_student(student_id, admin_id):
    student = Student.query.get(student_id)
    if not student:
        return None, 'Student not found'
    user = User.query.get(student.user_id)
    user.is_blacklisted = True
    user.is_active = False
    db.session.commit()

    # After db.session.commit() in BOTH, ADD:
    cache_clear_prefix('student:applications:' + str(student.user_id))
    invalidate_student_cache()
    log_action(admin_id, 'blacklisted_student', 'student', student_id)
    invalidate_student_cache()
    return student, None


def unblacklist_student(student_id, admin_id):
    student = Student.query.get(student_id)
    if not student:
        return None, 'Student not found'
    user = User.query.get(student.user_id)
    user.is_blacklisted = False
    user.is_active = True
    db.session.commit()
    # After db.session.commit() in BOTH, ADD:
    cache_clear_prefix('student:applications:' + str(student.user_id))
    invalidate_student_cache()    
    log_action(admin_id, 'unblacklisted_student', 'student', student_id)
    invalidate_student_cache()
    return student, None


def search_companies(query):
    cache_key = 'admin:search:companies:' + query.lower().strip()
    cached = cache_get(cache_key)
    if cached:
        return cached

    results = Company.query.filter(
        Company.company_name.ilike('%' + query + '%') |
        Company.industry.ilike('%' + query + '%') |
        Company.location.ilike('%' + query + '%')
    ).all()

    data = [c.to_dict() for c in results]
    cache_set(cache_key, data, SEARCH_EXPIRY)
    return data



def search_companies_advanced(query='', name='', industry=''):
    cache_key = 'admin:search:companies:' + (query + name + industry).lower().strip()
    cached = cache_get(cache_key)
    if cached:
        return cached

    q = Company.query

    if name:
        q = q.filter(Company.company_name.ilike('%' + name + '%'))
    elif industry:
        q = q.filter(Company.industry.ilike('%' + industry + '%'))
    elif query:
        q = q.filter(
            Company.company_name.ilike('%' + query + '%') |
            Company.industry.ilike('%' + query + '%') |
            Company.location.ilike('%' + query + '%')
        )

    results = q.all()
    data = []
    for c in results:
        d = c.to_dict()
        d['is_blacklisted'] = c.user.is_blacklisted if c.user else False
        d['is_active'] = c.user.is_active if c.user else True
        d['drive_count'] = c.drives.count()
        data.append(d)

    cache_set(cache_key, data, SEARCH_EXPIRY)
    return data


def search_students(query):
    cache_key = 'admin:search:students:' + query.lower().strip()
    cached = cache_get(cache_key)
    if cached:
        return cached

    results = Student.query.filter(
        Student.full_name.ilike('%' + query + '%') |
        Student.branch.ilike('%' + query + '%')
    ).all()

    data = [s.to_dict() for s in results]
    cache_set(cache_key, data, SEARCH_EXPIRY)
    return data


def get_admin_logs():
    cached = cache_get('admin:logs')
    if cached:
        return cached

    logs = AdminLog.query.order_by(AdminLog.timestamp.desc()).limit(100).all()
    data = [l.to_dict() for l in logs]
    cache_set('admin:logs', data, DASHBOARD_EXPIRY)
    return data


def invalidate_company_cache():
    cache_clear_prefix('admin:companies')
    cache_clear_prefix('admin:search:companies')
    cache_delete('admin:dashboard:stats')


def invalidate_student_cache():
    cache_clear_prefix('admin:students')
    cache_clear_prefix('admin:search:students')
    cache_delete('admin:dashboard:stats')


def invalidate_drive_cache():
    cache_clear_prefix('admin:drives')
    cache_clear_prefix('student:drives')
    cache_delete('admin:dashboard:stats')