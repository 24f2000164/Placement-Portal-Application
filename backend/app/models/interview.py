
from app.extensions import db
from datetime import datetime


class Interview(db.Model):
    __tablename__ = 'interviews'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, unique=True)
    scheduled_at = db.Column(db.DateTime)
    mode = db.Column(db.String(50))
    venue = db.Column(db.String(200))
    notes = db.Column(db.Text)
    result = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'mode': self.mode,
            'venue': self.venue,
            'notes': self.notes,
            'result': self.result,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'Interview application {self.application_id} result {self.result}'

