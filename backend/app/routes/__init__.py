def register_blueprints(app):
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.company import company_bp
    from app.routes.student import student_bp
    from app.routes.public    import public_bp
    from app.routes.analytics import analytics_bp

    app.register_blueprint(auth_bp,      url_prefix='/api/v1/auth')
    app.register_blueprint(admin_bp,     url_prefix='/api/v1/admin')
    app.register_blueprint(company_bp,   url_prefix='/api/v1/company')
    app.register_blueprint(student_bp,   url_prefix='/api/v1/student')
    app.register_blueprint(public_bp,    url_prefix='/api/v1/public')
    app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')