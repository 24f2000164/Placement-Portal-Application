from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity
from app.utils.decorators import role_required
from app.models.drive import PlacementDrive
from app.models.application import Application
from app.models.company import Company
from app.models.student import Student
from app.utils.cache import cache_get, cache_set
from datetime import datetime, timedelta
from collections import Counter

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/admin/overview', methods=['GET'])
@role_required('admin')
def admin_overview():
    cached = cache_get('analytics:admin:overview')
    if cached:
        return jsonify(cached), 200

    applications = Application.query.all()
    status_counts = Counter(a.status for a in applications)

    drives = PlacementDrive.query.filter_by(status='approved').all()
    skills_raw = []
    for d in drives:
        if d.skills_required:
            for s in d.skills_required.split(','):
                skills_raw.append(s.strip().lower())
    skills_counter = Counter(skills_raw)
    top_skills = [{'skill': k, 'count': v} for k, v in skills_counter.most_common(10)]

    companies = Company.query.filter_by(approval_status='approved').all()
    company_data = []
    for c in companies:
        drive_ids = [d.id for d in c.drives]
        total_apps = Application.query.filter(Application.drive_id.in_(drive_ids)).count() if drive_ids else 0
        selected   = Application.query.filter(Application.drive_id.in_(drive_ids), Application.status == 'selected').count() if drive_ids else 0
        company_data.append({
            'name':         c.company_name,
            'drives':       c.drives.count(),
            'applications': total_apps,
            'selected':     selected
        })
    company_data = sorted(company_data, key=lambda x: x['applications'], reverse=True)[:8]

    now = datetime.now()
    monthly = []
    for i in range(5, -1, -1):
        month_date  = now - timedelta(days=30 * i)
        month_label = month_date.strftime('%b %Y')
        start = datetime(month_date.year, month_date.month, 1)
        if month_date.month == 12:
            end = datetime(month_date.year + 1, 1, 1)
        else:
            end = datetime(month_date.year, month_date.month + 1, 1)

        month_apps      = Application.query.filter(Application.applied_at >= start, Application.applied_at < end).count()
        month_selected  = Application.query.filter(Application.applied_at >= start, Application.applied_at < end, Application.status == 'selected').count()
        month_drives    = PlacementDrive.query.filter(PlacementDrive.created_at >= start, PlacementDrive.created_at < end).count()

        monthly.append({
            'month':        month_label,
            'applications': month_apps,
            'selected':     month_selected,
            'drives':       month_drives
        })

    data = {
        'application_funnel': [
            {'stage': 'Applied',     'count': status_counts.get('applied', 0)},
            {'stage': 'Shortlisted', 'count': status_counts.get('shortlisted', 0)},
            {'stage': 'Interview',   'count': status_counts.get('interview', 0)},
            {'stage': 'Selected',    'count': status_counts.get('selected', 0)},
            {'stage': 'Placed',      'count': status_counts.get('placed', 0)}
        ],
        'top_skills':     top_skills,
        'company_stats':  company_data,
        'monthly_trends': monthly
    }

    cache_set('analytics:admin:overview', data, 120)
    return jsonify(data), 200


@analytics_bp.route('/company/overview', methods=['GET'])
@role_required('company')
def company_overview():
    user_id = get_jwt_identity()
    cache_key = 'analytics:company:' + str(user_id)
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached), 200

    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({'message': 'Company not found'}), 404

    drives   = PlacementDrive.query.filter_by(company_id=company.id).all()
    drive_ids = [d.id for d in drives]

    funnel = {'applied': 0, 'shortlisted': 0, 'interview': 0, 'selected': 0, 'placed': 0, 'rejected': 0}
    drive_stats = []

    for drive in drives:
        apps = Application.query.filter_by(drive_id=drive.id).all()
        for app in apps:
            if app.status in funnel:
                funnel[app.status] += 1

        drive_stats.append({
            'title':      drive.job_title,
            'applicants': len(apps),
            'selected':   sum(1 for a in apps if a.status == 'selected'),
            'status':     drive.status
        })

    data = {
        'funnel': [{'stage': k.capitalize(), 'count': v} for k, v in funnel.items()],
        'drive_stats': drive_stats
    }

    cache_set(cache_key, data, 120)
    return jsonify(data), 200




@analytics_bp.route('/cache/clear', methods=['POST'])
@role_required('admin')
def clear_analytics_cache():
    from app.utils.cache import cache_clear_prefix
    cache_clear_prefix('analytics:')
    cache_clear_prefix('public:')
    return jsonify({'message': 'Analytics cache cleared'}), 200




@analytics_bp.route('/student/overview', methods=['GET'])
@role_required('student')
def student_overview():
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'message': 'Student not found'}), 404

    applications = Application.query.filter_by(student_id=student.id).all()
    status_counts = Counter(a.status for a in applications)

    data = {
        'total_applied':     len(applications),
        'total_shortlisted': status_counts.get('shortlisted', 0),
        'total_interview':   status_counts.get('interview', 0),
        'total_selected':    status_counts.get('selected', 0),
        'total_rejected':    status_counts.get('rejected', 0),
        'status_breakdown': [
            {'label': k.capitalize(), 'count': v}
            for k, v in status_counts.items()
        ]
    }

    return jsonify(data), 200