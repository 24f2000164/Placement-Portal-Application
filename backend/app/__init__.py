import os
from flask import Flask
from app.config import config
from flask_cors import CORS
from app.extensions import db, migrate, jwt, mail, init_redis, init_celery
from flask import jsonify

from flask_cors import CORS

def create_app(config_name='default'):
    app = Flask(__name__, template_folder='templates')
    
    # Load config
    app.config.from_object(config[config_name])
    
    os.makedirs(os.path.join(app.root_path, '..', 'instance'),        exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'],                           exist_ok=True)
    os.makedirs(app.config['REPORTS_FOLDER'],                          exist_ok=True)
    os.makedirs(app.config['EXPORTS_FOLDER'],                          exist_ok=True)


    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
   
    init_celery(app)
    try:
        init_redis(app)    
    except Exception as e:
        print(f"Redis not available: {e}")
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Import all models (needed for migrations)
    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()         # Creates tables if not exist

    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    @app.errorhandler(413)
    def request_entity_too_large(e):
        return jsonify({'message': 'File too large. Maximum size is 10MB.'}), 413


    return app