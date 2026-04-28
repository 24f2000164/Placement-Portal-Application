
from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app('development')

with app.app_context():
    existing_admin = User.query.filter_by(role='admin').first()


    if existing_admin:
        
        print(f'Admin already exists: {existing_admin.email}')
       
     

    else:
        admin = User(
            email='bt23ece015@nituk.ac.in',
            role='admin',
            is_active=True,
            is_blacklisted=False
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()

        print('Admin created successfully')
        print('Email: bt23ece015@nituk.ac.in')
        print('Password: Admin@123')

