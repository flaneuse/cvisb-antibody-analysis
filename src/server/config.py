# APPLICATION SETTINGS
import os
basedir = os.path.abspath(os.path.dirname(__file__))
postgres_local_base = 'postgresql://laurahughes:@localhost/'
database_name = 'antibody_test'

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    """Development configuration."""
    DEVELOPMENT = True
    DEBUG = True
    # BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name
    FRONTEND_URL = 'http://localhost:4200/'


class TestingConfig(Config):
    TESTING = True
