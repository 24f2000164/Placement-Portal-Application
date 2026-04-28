from app.extensions import db
from datetime import datetime


class Application(db.Model):
    __tablename__ = 'applications'

    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    drive_id   = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    status     = db.Column(db.String(30), default='applied')
     
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    feedback = db.Column(db.Text, nullable=True)

    # ADD this column
     
    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_student_drive'),
    )

    interview = db.relationship('Interview', backref='application', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id':           self.id,
            'student_id':   self.student_id,
            'drive_id':     self.drive_id,
            'status':       self.status,
            'applied_at':   self.applied_at.isoformat(),
            'updated_at':   self.updated_at.isoformat(),
            'student_name': self.student.full_name if self.student else None,
            'drive_title':  self.drive.job_title if self.drive else None,
            'company_name': self.drive.company.company_name if self.drive and self.drive.company else None,
            'feedback': self.feedback,
        }

    def __repr__(self):
        return '<Application student=' + str(self.student_id) + ' drive=' + str(self.drive_id) + ' status=' + self.status + '>'