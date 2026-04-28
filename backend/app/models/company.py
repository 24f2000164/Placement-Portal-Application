
from app.extensions import db
from datetime import datetime


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    company_name = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(100))
    location = db.Column(db.String(150))
    website = db.Column(db.String(200))
    hr_contact = db.Column(db.String(100))
    hr_phone = db.Column(db.String(15))
    description = db.Column(db.Text)
    approval_status = db.Column(db.String(20), default='pending')
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationship
    drives = db.relationship('PlacementDrive', backref='company', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'industry': self.industry,
            'location': self.location,
            'website': self.website,
            'hr_contact': self.hr_contact,
            'hr_phone': self.hr_phone,
            'description': self.description,
            'approval_status': self.approval_status,
            'registered_at': self.registered_at.isoformat(),
            'email': self.user.email if self.user else None
        }

    def __repr__(self):
        return f'Company {self.company_name}'

