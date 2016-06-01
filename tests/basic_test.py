import unittest
from flask import current_app
from app import create_app, db
from mongoengine.connection import _get_db


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db = _get_db()

    def tearDown(self):
        db.connection.drop_database("SleepTight_db")
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])