import os
from app import app

_basedir = os.path.abspath(os.path.dirname(__file__) + '/../')

DEBUG = True
TESTING = False

ADMINS = frozenset(['super@admin.com'])
SECRET_KEY = '1234'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'colloid.db')

DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 16

CSRF_ENABLED = True
CSRF_SESSION_KEY = "123456"

CACHE_TYPE = 'simple'

LOG_FORMAT = "[%(asctime)-15s]:[%(levelname)s]:[%(name)s]:%(message)s"

try:
    from local_configs import *
except ImportError:
    import sys
    sys.stderr.write("No local config detected.")
