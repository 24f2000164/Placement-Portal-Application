
from app.extensions import db
from datetime import datetime


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_drives = db.Column(db.Integer, default=0)
    total_applications = db.Column(db.Integer, default=0)
    total_selected = db.Column(db.Integer, default=0)
    report_path = db.Column(db.String(300))
    sent_to_admin = db.Column(db.Boolean, default=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'month': self.month,
            'year': self.year,
            'total_drives': self.total_drives,
            'total_applications': self.total_applications,
            'total_selected': self.total_selected,
            'report_path': self.report_path,
            'sent_to_admin': self.sent_to_admin,
            'generated_at': self.generated_at.isoformat()
        }

    def __repr__(self):
        return f'Report {self.month} {self.year}'

