from app.extensions import celery, db
from app.models.drive import PlacementDrive
from app.models.application import Application
from app.models.interview import Interview
from app.models.student import Student
from app.models.user import User
from app.models.notification import Notification
from app.utils.mailer import send_email
from datetime import datetime, timedelta


@celery.task(name='app.tasks.reminders.send_interview_reminders')
def send_interview_reminders():
    now = datetime.now()
    next_day = now + timedelta(days=1)

    interviews = Interview.query.filter(
        Interview.scheduled_at >= now,
        Interview.scheduled_at <= next_day,
        Interview.result == 'pending'
    ).all()

    if not interviews:
        print('No interviews scheduled in next 24 hours')
        return 'No reminders sent'

    sent_count = 0

    for interview in interviews:
        application = interview.application
        if not application:
            continue

        student = application.student
        if not student:
            continue

        user = User.query.get(student.user_id)
        if not user or not user.is_active or user.is_blacklisted:
            continue

        drive = application.drive
        company_name = drive.company.company_name if drive and drive.company else 'N/A'
        job_title    = drive.job_title if drive else 'N/A'
        interview_time = interview.scheduled_at.strftime('%d %B %Y at %I:%M %p')
        venue        = interview.venue or 'To be communicated'

        subject = 'Interview Reminder: ' + job_title + ' at ' + company_name

        body = (
            'Dear ' + student.full_name + ',\n\n'
            'This is a reminder about your upcoming interview:\n\n'
            'Company   : ' + company_name + '\n'
            'Job Title : ' + job_title + '\n'
            'Mode      : ' + (interview.mode or 'N/A') + '\n'
            'Date/Time : ' + interview_time + '\n'
            'Venue     : ' + venue + '\n\n'
            'Please be prepared and log in to the Placement Portal for any updates.\n\n'
            'Best of luck!\n'
            'Placement Cell'
        )

        html_body = '''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
            <h2 style="color: #2c3e50;">Interview Reminder</h2>
            <p>Dear <strong>{name}</strong>,</p>
            <p>This is a reminder about your upcoming interview:</p>
            <table style="width:100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="background:#f4f4f4;">
                    <td style="padding:10px; font-weight:bold;">Company</td>
                    <td style="padding:10px;">{company}</td>
                </tr>
                <tr>
                    <td style="padding:10px; font-weight:bold;">Job Title</td>
                    <td style="padding:10px;">{job}</td>
                </tr>
                <tr style="background:#f4f4f4;">
                    <td style="padding:10px; font-weight:bold;">Mode</td>
                    <td style="padding:10px;">{mode}</td>
                </tr>
                <tr>
                    <td style="padding:10px; font-weight:bold;">Date and Time</td>
                    <td style="padding:10px; color:#e74c3c;"><strong>{time}</strong></td>
                </tr>
                <tr style="background:#f4f4f4;">
                    <td style="padding:10px; font-weight:bold;">Venue</td>
                    <td style="padding:10px;">{venue}</td>
                </tr>
            </table>
            <p>Please be prepared and log in to the Placement Portal for any updates.</p>
            <p style="color:#27ae60;"><strong>Best of luck!</strong></p>
            <p style="color:#999; font-size:12px;">Regards,<br/>Placement Cell</p>
        </div>
        '''.format(
            name=student.full_name,
            company=company_name,
            job=job_title,
            mode=interview.mode or 'N/A',
            time=interview_time,
            venue=venue
        )

        notif = Notification(
            user_id=user.id,
            message='Interview reminder: ' + job_title + ' at ' + company_name + ' on ' + interview_time,
            type='email'
        )
        db.session.add(notif)

        if user.email:
            send_email(user.email, subject, body, html_body)
            sent_count += 1

    db.session.commit()
    print('Sent ' + str(sent_count) + ' interview reminders')
    return 'Sent ' + str(sent_count) + ' reminders'


@celery.task(name='app.tasks.reminders.send_deadline_reminders')
def send_deadline_reminders():
    now = datetime.now()
    in_3_days = now + timedelta(days=3)

    drives = PlacementDrive.query.filter(
        PlacementDrive.status == 'approved',
        PlacementDrive.application_deadline >= now,
        PlacementDrive.application_deadline <= in_3_days
    ).all()

    if not drives:
        print('No deadlines in next 3 days')
        return 'No deadline reminders sent'

    students = Student.query.all()
    sent_count = 0

    for student in students:
        user = User.query.get(student.user_id)
        if not user or not user.is_active or user.is_blacklisted:
            continue

        for drive in drives:
            already = Application.query.filter_by(
                student_id=student.id,
                drive_id=drive.id
            ).first()
            if already:
                continue

            eligible = True
            if drive.min_cgpa and student.cgpa and student.cgpa < drive.min_cgpa:
                eligible = False
            if drive.eligible_branches and student.branch:
                allowed = [b.strip().upper() for b in drive.eligible_branches.split(',')]
                if student.branch.upper() not in allowed:
                    eligible = False

            if not eligible:
                continue

            deadline_str = drive.application_deadline.strftime('%d %B %Y')
            company_name = drive.company.company_name if drive.company else 'N/A'

            subject = 'Deadline Reminder: Apply to ' + drive.job_title + ' before ' + deadline_str

            body = (
                'Dear ' + student.full_name + ',\n\n'
                'The application deadline for the following drive is approaching:\n\n'
                'Job Title : ' + drive.job_title + '\n'
                'Company   : ' + company_name + '\n'
                'Deadline  : ' + deadline_str + '\n\n'
                'Log in to the Placement Portal and apply now.\n\n'
                'Regards,\nPlacement Cell'
            )

            notif = Notification(
                user_id=user.id,
                message='Deadline reminder: ' + drive.job_title + ' closes on ' + deadline_str,
                type='email'
            )
            db.session.add(notif)

            if user.email:
                send_email(user.email, subject, body)
                sent_count += 1

    db.session.commit()
    print('Sent ' + str(sent_count) + ' deadline reminders')
    return 'Sent ' + str(sent_count) + ' deadline reminders'