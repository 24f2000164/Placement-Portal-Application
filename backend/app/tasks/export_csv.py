from app.extensions import celery
from app.models.student import Student
from app.models.company import Company
from app.models.application import Application
from app.models.user import User
from app.utils.mailer import send_email
from datetime import datetime
import csv
import io


@celery.task(name='app.tasks.export_csv.export_student_applications')
def export_student_applications(user_id):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return 'Student not found'

    user = User.query.get(user_id)
    if not user:
        return 'User not found'

    applications = Application.query.filter_by(
        student_id=student.id
    ).order_by(Application.applied_at.desc()).all()

    # Build CSV in memory — no file saved to disk
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Application ID',
        'Student ID',
        'Student Name',
        'Company Name',
        'Drive Title',
        'Application Status',
        'Applied Date',
        'Interview Mode',
        'Interview Date',
        'Interview Result',
        'Salary',
        'Location'
    ])

    for app in applications:
        company_name     = ''
        drive_title      = ''
        interview_mode   = ''
        interview_date   = ''
        interview_result = ''
        salary           = ''
        location         = ''

        if app.drive:
            drive_title = app.drive.job_title
            salary      = app.drive.salary or ''
            location    = app.drive.location or ''
            if app.drive.company:
                company_name = app.drive.company.company_name

        if app.interview:
            interview_mode   = app.interview.mode or ''
            interview_result = app.interview.result or ''
            if app.interview.scheduled_at:
                interview_date = app.interview.scheduled_at.strftime('%d-%m-%Y %H:%M')

        writer.writerow([
            app.id,
            student.id,
            student.full_name,
            company_name,
            drive_title,
            app.status,
            app.applied_at.strftime('%d-%m-%Y') if app.applied_at else '',
            interview_mode,
            interview_date,
            interview_result,
            salary,
            location
        ])

    csv_content = output.getvalue()
    output.close()

    filename = 'placement_history_' + datetime.now().strftime('%Y%m%d%H%M%S') + '.csv'

    subject = 'Your Placement History Export'
    html_body = '''
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;
                padding:20px;border:1px solid #eee;border-radius:8px;">
        <h2 style="color:#27ae60;">Placement History Export</h2>
        <p>Dear <strong>{name}</strong>,</p>
        <p>Please find your placement application history attached to this email.</p>
        <table style="width:100%;border-collapse:collapse;margin:20px 0;">
            <tr style="background:#f4f4f4;">
                <td style="padding:10px;font-weight:bold;">Total Records</td>
                <td style="padding:10px;">{count}</td>
            </tr>
            <tr>
                <td style="padding:10px;font-weight:bold;">Generated On</td>
                <td style="padding:10px;">{date}</td>
            </tr>
        </table>
        <p style="color:#999;font-size:12px;">Regards,<br/>Placement Portal</p>
    </div>
    '''.format(
        name=student.full_name,
        count=len(applications),
        date=datetime.now().strftime('%d %B %Y, %H:%M')
    )

    body = (
        'Dear ' + student.full_name + ',\n\n'
        'Please find your placement application history attached.\n\n'
        'Total records: ' + str(len(applications)) + '\n\n'
        'Regards,\nPlacement Portal'
    )

    if user.email:
        send_email(
            user.email,
            subject,
            body,
            html_body=html_body,
            attachments=[(filename, 'text/csv', csv_content.encode('utf-8'))]
        )

    print('CSV export emailed to student ' + str(student.id) + ' - ' + str(len(applications)) + ' records')
    return {'status': 'done', 'records': len(applications)}


@celery.task(name='app.tasks.export_csv.export_company_applications')
def export_company_applications(user_id):
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return 'Company not found'

    user = User.query.get(user_id)
    if not user:
        return 'User not found'

    from app.models.drive import PlacementDrive
    drives    = PlacementDrive.query.filter_by(company_id=company.id).all()
    drive_ids = [d.id for d in drives]

    applications = []
    if drive_ids:
        applications = Application.query.filter(
            Application.drive_id.in_(drive_ids)
        ).order_by(Application.applied_at.desc()).all()

    # Build CSV in memory — no file saved to disk
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Application ID',
        'Student Name',
        'Student Branch',
        'Student CGPA',
        'Drive Title',
        'Application Status',
        'Applied Date',
        'Interview Mode',
        'Interview Date',
        'Interview Result'
    ])

    for app in applications:
        student_name     = app.student.full_name if app.student else ''
        student_branch   = app.student.branch if app.student else ''
        student_cgpa     = app.student.cgpa if app.student else ''
        drive_title      = app.drive.job_title if app.drive else ''
        interview_mode   = ''
        interview_date   = ''
        interview_result = ''

        if app.interview:
            interview_mode   = app.interview.mode or ''
            interview_result = app.interview.result or ''
            if app.interview.scheduled_at:
                interview_date = app.interview.scheduled_at.strftime('%d-%m-%Y %H:%M')

        writer.writerow([
            app.id,
            student_name,
            student_branch,
            student_cgpa,
            drive_title,
            app.status,
            app.applied_at.strftime('%d-%m-%Y') if app.applied_at else '',
            interview_mode,
            interview_date,
            interview_result
        ])

    csv_content = output.getvalue()
    output.close()

    filename = 'applications_export_' + datetime.now().strftime('%Y%m%d%H%M%S') + '.csv'

    subject = 'Your Applications Export'
    html_body = '''
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;
                padding:20px;border:1px solid #eee;border-radius:8px;">
        <h2 style="color:#27ae60;">Applications Export</h2>
        <p>Dear <strong>{name}</strong>,</p>
        <p>Please find your applications export attached to this email.</p>
        <table style="width:100%;border-collapse:collapse;margin:20px 0;">
            <tr style="background:#f4f4f4;">
                <td style="padding:10px;font-weight:bold;">Total Records</td>
                <td style="padding:10px;">{count}</td>
            </tr>
            <tr>
                <td style="padding:10px;font-weight:bold;">Generated On</td>
                <td style="padding:10px;">{date}</td>
            </tr>
        </table>
        <p style="color:#999;font-size:12px;">Regards,<br/>Placement Portal</p>
    </div>
    '''.format(
        name=company.company_name,
        count=len(applications),
        date=datetime.now().strftime('%d %B %Y, %H:%M')
    )

    body = (
        'Dear ' + company.company_name + ',\n\n'
        'Please find your applications export attached.\n\n'
        'Total records: ' + str(len(applications)) + '\n\n'
        'Regards,\nPlacement Portal'
    )

    if user.email:
        send_email(
            user.email,
            subject,
            body,
            html_body=html_body,
            attachments=[(filename, 'text/csv', csv_content.encode('utf-8'))]
        )

    print('CSV export emailed to company ' + str(company.id) + ' - ' + str(len(applications)) + ' records')
    return {'status': 'done', 'records': len(applications)}