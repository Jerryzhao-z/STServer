from flask import jsonify, request, current_app, url_for, abort, g, redirect
from . import api
from ..models import User
from .authentication import auth
from bson.objectid import ObjectId
try:
	import cPickle as pickle 
except ImportError:
	import pickle
import requests, json, base64
# 25/5/2016 11:48
#get id
# curl -u <username>:<password> -i -X GET -H "Content-Type: application/json" http://sleeptight2016.herokuapp.com/api/v1.0/users/<id>
@api.route('/users/<id>/')
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
@api.route('/users/delete/<id>/')
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
@api.route('/users/fitbit/auth/')
@auth.login_required
def request_fibit_auth():
	head_url = "https://www.fitbit.com/oauth2/authorize?"
	response_type = "code"
	client_id = "227TD3"
	redirect_uri = "http%3A%2F%2Fsleeptight2016.herokuapp.com%2Fapi%2Fv1.0%2Fusers%2Ffitbit%2Fcallback%2F"
	#redirect_uri = "http%3A%2F%2Fsleeptight2016.herokuapp.com%2F"
	scope = "heartrate%20location%20sleep"
	expires_in = "2592000" # 1 month
	state = str(g.current_user.id)
	return redirect(head_url+"response_type="+response_type+"&client_id="+client_id+"&redirect_uri="+redirect_uri+"&scope="+scope+"&expires_in="+expires_in+"&state="+state)


@api.route('/users/fitbit/callback/')
def callback_fitbit_auth():
	state_id = request.args.get("state")
	user = User.objects(id=ObjectId(state_id)).first() 
	code = request.args.get("code")
	user.update(fitbit_callback_code = code)
	#return jsonify({'code': user.fitbit_callback_code}), 200
	client_id = "227TD3"
	client_secret = "47fb319850e594fec1a0aa88de295898"
	request_body = "clientId=22zMTX&grant_type=authorization_code&redirect_uri=http%3A%2F%2Fsleeptight2016.herokuapp.com%2Fapi%2Fv1.0%2Fusers%2Ffitbit%2Fcallback%2F&code="+code
	#request_body = "clientId=22zMTX&grant_type=authorization_code&redirect_uri=http%3A%2F%2Fsleeptight2016.herokuapp.com%2F&code="+code
	request_headers = {'Authorization':'Basic '+base64.b64encode(client_id+":"+client_secret), 'Content-type':'application/x-www-form-urlencoded' }
	response_curl = requests.post("https://api.fitbit.com/oauth2/token", data=request_body, headers=request_headers)
	response_dictionary = json.loads(response_curl.text)
	access_token = response_dictionary["access_token"]
	user.update(fitbit_access_token=access_token)
	token_type = response_dictionary["token_type"]
	user.update(fitbit_token_type=token_type)
	fitbit_user_id = response_dictionary["user_id"]
	user.update(fitbit_user_id=fitbit_user_id)
	fitbit_refresh_token = response_dictionary["refresh_token"]
	user.update(fitbit_refresh_token=fitbit_refresh_token)	
	#return jsonify({'state_id': state_id, 'token_type':token_type, 'fitbit_user_id':fitbit_user_id}), 200
	return redirect("SleepTight://Main:8000/mypath?key=mykey")

#def refresh_token()

#def get_access_token()
#TODO
@api.route('/users/fitbit/sleeps/')
@auth.login_required
def get_sleep_log():
	# verify is there sleep_log of the day
	user = g.current_user
	response_curl = requests.get("url", headers={'Authorization': user.fitbit_token_type+" "+user.fitbit_access_token}) 
	return response_curl.text
	#TODO: traitment of data
	#TODO: return the data to android
	#return jsonify()
# generation de token fichier: authentification.py
