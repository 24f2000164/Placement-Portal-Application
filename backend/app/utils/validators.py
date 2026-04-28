import re


def validate_email(email):
    if not email:
        return False
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def validate_password(password):
    if not password:
        return False, 'Password is required'
    if len(password) < 6:
        return False, 'Password must be at least 6 characters'
    return True, ''


def validate_cgpa(cgpa):
    try:
        val = float(cgpa)
        if val < 0 or val > 10:
            return False, 'CGPA must be between 0 and 10'
        return True, ''
    except Exception:
        return False, 'CGPA must be a valid number'


def validate_phone(phone):
    if not phone:
        return True, ''
    pattern = r'^\+?[\d\s\-]{7,15}$'
    if not re.match(pattern, phone):
        return False, 'Invalid phone number format'
    return True, ''


def validate_url(url):
    if not url:
        return True, ''
    pattern = r'^https?://.+'
    if not re.match(pattern, url):
        return False, 'URL must start with http:// or https://'
    return True, ''


def validate_registration(data, role):
    errors = []

    if not data.get('email'):
        errors.append('Email is required')
    elif not validate_email(data['email']):
        errors.append('Invalid email format')

    if not data.get('password'):
        errors.append('Password is required')
    else:
        valid, msg = validate_password(data['password'])
        if not valid:
            errors.append(msg)

    if role == 'student':
        if not data.get('full_name'):
            errors.append('Full name is required')

        if data.get('cgpa'):
            valid, msg = validate_cgpa(data['cgpa'])
            if not valid:
                errors.append(msg)

        if data.get('phone'):
            valid, msg = validate_phone(data['phone'])
            if not valid:
                errors.append(msg)

        if data.get('year'):
            try:
                year = int(data['year'])
                if year < 1 or year > 4:
                    errors.append('Year must be between 1 and 4')
            except Exception:
                errors.append('Year must be a number')

    if role == 'company':
        if not data.get('company_name'):
            errors.append('Company name is required')

        if data.get('website'):
            valid, msg = validate_url(data['website'])
            if not valid:
                errors.append(msg)

        if data.get('hr_phone'):
            valid, msg = validate_phone(data['hr_phone'])
            if not valid:
                errors.append(msg)

    return errors


def validate_drive_data(data):
    errors = []

    if not data.get('job_title'):
        errors.append('Job title is required')

    if data.get('min_cgpa'):
        valid, msg = validate_cgpa(data['min_cgpa'])
        if not valid:
            errors.append(msg)

    if data.get('eligible_year'):
        try:
            year = int(data['eligible_year'])
            if year < 1 or year > 4:
                errors.append('Eligible year must be between 1 and 4')
        except Exception:
            errors.append('Eligible year must be a number')

    if data.get('application_deadline'):
        from datetime import datetime
        try:
            deadline = datetime.fromisoformat(data['application_deadline'])
            if deadline < datetime.utcnow():
                errors.append('Application deadline cannot be in the past')
        except Exception:
            errors.append('Invalid deadline format. Use YYYY-MM-DD')

    return errors


def validate_status_update(status, allowed_statuses):
    if status not in allowed_statuses:
        return False, 'Invalid status. Allowed values: ' + ', '.join(allowed_statuses)
    return True, ''