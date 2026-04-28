from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from celery import Celery
import redis

# Shared instances - import these everywhere, never re-create
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
celery   = Celery()

# Redis client - initialized in create_app
redis_client = None

def init_redis(app):
    global redis_client
    try:
        client = redis.from_url(
            app.config['REDIS_URL'],
            decode_responses=True,
            socket_connect_timeout=2,   # fail fast if Redis is not running
            socket_timeout=2
        )
        client.ping()                   # actually verify the connection works
        redis_client = client
        print('Redis connected: ' + app.config['REDIS_URL'])
    except Exception as e:
        redis_client = None
        print('Redis unavailable — caching disabled: ' + str(e))
    return redis_client

def init_celery(app):
    celery.conf.broker_url        = app.config['CELERY_BROKER_URL']
    celery.conf.result_backend    = app.config['CELERY_RESULT_BACKEND']
    celery.conf.timezone          = app.config.get('CELERY_TIMEZONE', 'Asia/Kolkata')
    celery.conf.enable_utc        = False

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery