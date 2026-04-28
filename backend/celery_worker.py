from dotenv import load_dotenv
load_dotenv() 
from app import create_app
from app.extensions import celery
from celery.schedules import crontab

flask_app = create_app('development')
flask_app.app_context().push()

celery.conf.beat_schedule = {
    'daily-interview-reminder': {
        'task': 'app.tasks.reminders.send_interview_reminders',
        'schedule': crontab(hour=8, minute=0),
    },
     'daily-deadline-reminder': {                              # ADD THIS
        'task': 'app.tasks.reminders.send_deadline_reminders',
        'schedule': crontab(hour=9, minute=0),                # runs daily at 9 AM
    },
    'monthly-placement-report': {
        'task': 'app.tasks.monthly_report.generate_monthly_report',
        'schedule': crontab(hour=6, minute=0, day_of_month=1),
    },
}

from app.tasks import reminders, monthly_report, export_csv