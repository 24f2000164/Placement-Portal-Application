
from app.extensions import db
from datetime import datetime


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    branch = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    year = db.Column(db.Integer)
    skills = db.Column(db.Text)
    resume_path = db.Column(db.String(300))
    experience = db.Column(db.String(200))  # e.g. "Fresher", "6 months internship"
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    linkdin_url=db.Column(db.String(300),nullable=True)

    # relationship
    applications = db.relationship('Application', backref='student', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'phone': self.phone,
            'branch': self.branch,
            'cgpa': self.cgpa,
            'year': self.year,
            'skills': self.skills,
            'resume_path': self.resume_path,
            'experience': self.experience,
            'email': self.user.email if self.user else None,
            'linkdin_url': self.linkdin_url if self.user else None
        }

    def __repr__(self):
        return f'Student {self.full_name}'

