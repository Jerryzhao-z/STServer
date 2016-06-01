import unittest
import json
import re
from base64 import b64encode
from flask import url_for
from app import create_app, db
from app.models import User
from mongoengine import _get_db

class APITestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing api')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db = _get_db()
		self.client = self.app.test_client(use_cookies = True)

	def tearDown(self):
        		db.connection.drop_database("SleepTight_db")
		self.app_context.pop()

	def get_api_headers(self, username, password):
		return {
			'Authorization': 'Basic ' + b64encode(
			(username + ':' + password).encode('utf-8')).decode('utf-8'),
			'Accept': 'application/json',
			'Content-Type': 'application/json'
			}
       	  def test_404(self):
		response = self.client.get(
			'/wrong/url',
			headers=self.get_api_headers('username', 'password'))
		self.assertTrue(response.status_code == 404)
		json_response = json.loads(response.data.decode('utf-8'))
		self.assertTrue(json_response['error'] == 'not found')

    	# def test_no_auth(self):
     #    		response = self.client.get(url_for('api.get_posts'),
     #                               content_type='application/json')
     #    		self.assertTrue(response.status_code == 200)

