import unittest
import os
import tempfile

from app import app


class DbTestCase(unittest.TestCase):
    """The base db test case"""

    def setUp(self):
        """Executes before each test"""

        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = '1234'
        self.client = app.test_client()
        self.app = app

    def tearDown(self):
        """Executes after each tests"""

        os.close(self.db_fd)
        os.unlink(self.app.config['DATABASE'])


class ModelTestCase(DbTestCase):
    pass
