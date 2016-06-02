from flask import jsonify, request, current_app, url_for, abort, g, redirect
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
# curl -u <username>:<password> -i -X GET -H "Content-Type: application/json" http://sleeptight2016.herokuapp.com/api/v1.0/users/<id>
@api.route('/users/<id>')
@auth.login_required
def get_user(id):
	id = ObjectId(id)
	user = User.objects(id=id).first()
	if user is None:
		abort(404)#user doesn't existe
	return jsonify({'username':user.username, 'email':user.email})
# sign up 
# curl -i -X POST -H "Content-Type: application/json" -d '{"username":"<username>", "password":"<password>"}' http://sleeptight2016.herokuapp.com/api/v1.0/users/
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
# curl -u <username>:<password> -i -X get -H "Content-Type: application/json" http://sleeptight2016.herokuapp.com/api/v1.0/users/delete/<id>
@api.route('/users/delete/<id>')
@auth.login_required
def delete_user(id):
	if User.objects(id=ObjectId(id)).first() is None:
		res = id+" doesn't exist"
		return jsonify({'result': res}), 204
	elif g.current_user.id != ObjectId(id):
		res = "you aren't authorized to delete the user"
		return jsonify({'result': res}), 202
	else:
		g.current_user.delete();
		res = "id has been deleted"
		return jsonify({'result': res}), 200
# modify
#gestion de token

#fitbit
#redirect the user to Fitbit OAuth 2.0
@api.route('/users/fitbit/permission/')
@auth.login_required
def get_permission_fitbit():
	client_id = "227MTX"
	response_type = "code"
	scope = "heartrate%20sleep%20location"
	redirect_uri = "http%3A%2F%2Fsleeptight2016.herokuapp.com%2F"
	expires_in = "604800" # 1 week
	state = str(g.current_user.id)
	return redirect("https://www.fitbit.com/oauth2/authorize?response_type="+response_type+"&client_id="+client_id+"&redirect_uri="+redirect_uri+"&scope="+scope+"&expires_in="+expires_in+"&state="+state)

	
# generation de token fichier: authentification.py
