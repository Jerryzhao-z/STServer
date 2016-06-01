from flask import jsonify, request, current_app, url_for, abort, g
from . import api
from ..models import User
from .authentication import auth
from bson.objectid import ObjectId
try:
	import cPickle as pickle 
except ImportError:
	import pickle

# 25/5/2016 11:48
#get id
@api.route('/users/<id>')
@auth.login_required
def get_user(id):
	id = ObjectId(id)
	user = User.objects(id=id).first()
	if user is None:
		abort(404)#user doesn't existe
	return jsonify({'username':user.username, 'email':user.email})
# sign up 
@api.route('/users/', methods =['POST'])
def new_user():
	 username = request.json.get('username')
	 password = request.json.get('password')
	 #email = request.json.get('email')
	 if username is None or password is None:
	 	abort(400)#missing arguments
	 if User.objects(username=username).first() is not None:
	 	abort(400)#existing user
	 user = User(username = username)
	 user.set_up_password(password = password)
	 user.save()
	 id = User.objects(username=username).first().id
	 return jsonify({'username': user.username, 'id': str(id)}), 201
#
# login
# in file authentication.py, test with command: curl -X POST -u "username:password" url_ressource
# miguelgrinberg restful-authentication-with-flask

# logout
#we don't need logout, because in API Restful, we don't really create login

# delete account
@api.route('/users/delete/<id>')
@auth.login_required
def delete_user(id):
	if User.objects(id=ObjectId(id)).first() is None:
		return id+" doesn't exist"
	if g.current_user.id != ObjectId(id):
		return "you aren't authorized to delete the user"
	else:
		g.current_user.delete();
		return "id has been deleted"
# modify
#gestion de token
# generation de token fichier: authentification.py
