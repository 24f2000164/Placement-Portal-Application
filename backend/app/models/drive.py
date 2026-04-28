
from app.extensions import db
from datetime import datetime


class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text)
    eligible_branches = db.Column(db.String(300))
    min_cgpa = db.Column(db.Float, default=0.0)
    eligible_year = db.Column(db.Integer)
    salary = db.Column(db.String(100))
    location = db.Column(db.String(150))
    skills_required = db.Column(db.Text)
    application_deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationship
    applications = db.relationship('Application', backref='drive', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.company_name if self.company else None,
            'job_title': self.job_title,
            'job_description': self.job_description,
            'eligible_branches': self.eligible_branches,
            'min_cgpa': self.min_cgpa,
            'eligible_year': self.eligible_year,
            'salary': self.salary,
            'location': self.location,
            'skills_required': self.skills_required,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'applicant_count': self.applications.count()
        }

    def __repr__(self):
        return f'Drive {self.job_title} company {self.company_id}'

