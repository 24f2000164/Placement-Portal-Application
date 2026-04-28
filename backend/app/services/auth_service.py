from app.extensions import db
from app.models.user import User
from app.models.student import Student
from app.models.company import Company
from flask_jwt_extended import create_access_token


def register_student(data):
    existing = User.query.filter_by(email=data['email']).first()
    if existing:
        return None, 'Email already registered'

    user = User(email=data['email'], role='student')
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()

    student = Student(
        user_id=user.id,
        full_name=data.get('full_name', ''),
        phone=data.get('phone', ''),
        branch=data.get('branch', ''),
        cgpa=data.get('cgpa', 0.0),
        year=data.get('year', 1)
    )
    db.session.add(student)
    db.session.commit()
    print(f" STUDENT SAVED: id={user.id} email={user.email}")
    return user, None


def register_company(data):
    existing = User.query.filter_by(email=data['email']).first()
    if existing:
        return None, 'Email already registered'

    user = User(email=data['email'], role='company')
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()

    company = Company(
        user_id=user.id,
        company_name=data.get('company_name', ''),
        industry=data.get('industry', ''),
        location=data.get('location', ''),
        website=data.get('website', ''),
        hr_contact=data.get('hr_contact', ''),
        hr_phone=data.get('hr_phone', ''),
        description=data.get('description', ''),
        approval_status='pending'
    )
    db.session.add(company)
    db.session.commit()
    return user, None


def login_user(email, password):
    user = User.query.filter_by(email=email).first()

    if not user:
        return None, None, 'Invalid email or password'

    if not user.check_password(password):
        return None, None, 'Invalid email or password'

    if user.is_blacklisted:
        return None, None, 'Your account has been blacklisted'

    if not user.is_active:
        return None, None, 'Your account is deactivated'

    # token = create_access_token(identity=user.id)
    token = create_access_token(identity=str(user.id))
    return user, token, None


def get_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return None

    profile = user.to_dict()

    if user.role == 'student' and user.student:
        profile['profile'] = user.student.to_dict()

    if user.role == 'company' and user.company:
        profile['profile'] = user.company.to_dict()

    return profile