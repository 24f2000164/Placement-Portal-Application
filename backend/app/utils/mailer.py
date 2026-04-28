from flask_mail import Message
from app.extensions import mail


def send_email(to, subject, body, html_body=None, attachments=None):
    try:
        recipients = [to] if isinstance(to, str) else to
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=body,
            html=html_body
        )
        # attachments: list of (filename, mimetype, data_bytes)
        if attachments:
            for filename, mimetype, data in attachments:
                msg.attach(filename, mimetype, data)
        mail.send(msg)
        print('Email sent to: ' + str(recipients))
        return True
    except Exception as e:
        print('Mail error: ' + str(e))
        return False


def send_bulk_email(recipients, subject, body, html_body=None):
    count = 0
    for r in recipients:
        if send_email(r, subject, body, html_body):
            count += 1
    return count


def build_reminder_email(student_name, job_title, company_name,
                          interview_time, mode, venue):
    subject = 'Interview Reminder: ' + job_title + ' at ' + company_name

    body = (
        'Dear ' + student_name + ',\n\n'
        'This is a reminder about your upcoming interview:\n\n'
        'Company   : ' + company_name + '\n'
        'Job Title : ' + job_title + '\n'
        'Mode      : ' + (mode or 'N/A') + '\n'
        'Date/Time : ' + interview_time + '\n'
        'Venue     : ' + (venue or 'To be communicated') + '\n\n'
        'Please be prepared and log in to the Placement Portal for updates.\n\n'
        'Best of luck!\nPlacement Cell'
    )

    html_body = '''
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;
                padding:20px;border:1px solid #eee;border-radius:8px;">
        <h2 style="color:#2c3e50;">Interview Reminder</h2>
        <p>Dear <strong>{name}</strong>,</p>
        <p>This is a reminder about your upcoming interview:</p>
        <table style="width:100%;border-collapse:collapse;margin:20px 0;">
            <tr style="background:#f4f4f4;">
                <td style="padding:10px;font-weight:bold;">Company</td>
                <td style="padding:10px;">{company}</td>
            </tr>
            <tr>
                <td style="padding:10px;font-weight:bold;">Job Title</td>
                <td style="padding:10px;">{job}</td>
            </tr>
            <tr style="background:#f4f4f4;">
                <td style="padding:10px;font-weight:bold;">Mode</td>
                <td style="padding:10px;">{mode}</td>
            </tr>
            <tr>
                <td style="padding:10px;font-weight:bold;">Date and Time</td>
                <td style="padding:10px;color:#e74c3c;"><strong>{time}</strong></td>
            </tr>
            <tr style="background:#f4f4f4;">
                <td style="padding:10px;font-weight:bold;">Venue</td>
                <td style="padding:10px;">{venue}</td>
            </tr>
        </table>
        <p>Please log in to the Placement Portal for any updates.</p>
        <p style="color:#27ae60;"><strong>Best of luck!</strong></p>
        <p style="color:#999;font-size:12px;">Regards,<br/>Placement Cell</p>
    </div>
    '''.format(
        name=student_name,
        company=company_name,
        job=job_title,
        mode=mode or 'N/A',
        time=interview_time,
        venue=venue or 'To be communicated'
    )

    return subject, body, html_body


def build_deadline_email(student_name, job_title, company_name, deadline_str):
    subject = 'Deadline Reminder: Apply to ' + job_title + ' before ' + deadline_str

    body = (
        'Dear ' + student_name + ',\n\n'
        'The application deadline for the following drive is approaching:\n\n'
        'Job Title : ' + job_title + '\n'
        'Company   : ' + company_name + '\n'
        'Deadline  : ' + deadline_str + '\n\n'
        'Log in to the Placement Portal and apply now.\n\n'
        'Regards,\nPlacement Cell'
    )

    html_body = '''
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;
                padding:20px;border:1px solid #eee;border-radius:8px;">
        <h2 style="color:#e67e22;">Application Deadline Reminder</h2>
        <p>Dear <strong>{name}</strong>,</p>
        <p>The application deadline for the following drive is approaching:</p>
        <table style="width:100%;border-collapse:collapse;margin:20px 0;">
            <tr style="background:#f4f4f4;">
                <td style="padding:10px;font-weight:bold;">Job Title</td>
                <td style="padding:10px;">{job}</td>
            </tr>
            <tr>
                <td style="padding:10px;font-weight:bold;">Company</td>
                <td style="padding:10px;">{company}</td>
            </tr>
            <tr style="background:#f4f4f4;">
                <td style="padding:10px;font-weight:bold;">Deadline</td>
                <td style="padding:10px;color:#e74c3c;"><strong>{deadline}</strong></td>
            </tr>
        </table>
        <p>Log in to the Placement Portal and apply now!</p>
        <p style="color:#999;font-size:12px;">Regards,<br/>Placement Cell</p>
    </div>
    '''.format(
        name=student_name,
        job=job_title,
        company=company_name,
        deadline=deadline_str
    )

    return subject, body, html_body


def build_export_ready_email(student_name, filename, record_count):
    subject = 'Your Application Export is Ready'

    body = (
        'Dear ' + student_name + ',\n\n'
        'Your placement application history export is ready.\n\n'
        'Total records exported: ' + str(record_count) + '\n'
        'Filename: ' + filename + '\n\n'
        'You can download it from your dashboard under Placement History.\n\n'
        'Regards,\nPlacement Portal'
    )

    html_body = '''
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;
                padding:20px;border:1px solid #eee;border-radius:8px;">
        <h2 style="color:#27ae60;">Your Export is Ready!</h2>
        <p>Dear <strong>{name}</strong>,</p>
        <p>Your placement application history export has been generated.</p>
        <table style="width:100%;border-collapse:collapse;margin:20px 0;">
            <tr style="background:#f4f4f4;">
                <td style="padding:10px;font-weight:bold;">Total Records</td>
                <td style="padding:10px;">{count}</td>
            </tr>
            <tr>
                <td style="padding:10px;font-weight:bold;">Filename</td>
                <td style="padding:10px;">{filename}</td>
            </tr>
        </table>
        <p>Log in to your dashboard and go to <strong>Placement History</strong> to download.</p>
        <p style="color:#999;font-size:12px;">Regards,<br/>Placement Portal</p>
    </div>
    '''.format(
        name=student_name,
        count=record_count,
        filename=filename
    )

    return subject, body, html_body