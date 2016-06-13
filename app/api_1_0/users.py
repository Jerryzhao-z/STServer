from flask import jsonify, request, current_app, url_for, abort, g, redirect
from . import api
from ..models import User
from .authentication import auth, verify_password
from bson.objectid import ObjectId
try:
	import cPickle as pickle 
except ImportError:
	import pickle
import requests, json, base64, re

client_id = "227TCL"
client_secret = "eac29ba018dd1e0e663b7316aa3098a1"
scope = "heartrate%20location%20sleep"
expires_in = "2592000" # 1 month
redirect_uri = "http%3A%2F%2Fsleeptight2016.herokuapp.com%2Fapi%2Fv1.0%2Fusers%2Ffitbit%2Fcallback"
#redirect_uri = "http%3A%2F%2Fsleeptight2016.herokuapp.com%2F"
# 25/5/2016 11:48
#get id
# curl -u <username>:<password> -i -X GET -H "Content-Type: application/json" http://sleeptight2016.herokuapp.com/api/v1.0/users/<id>
@api.route('/users/<id>/')
@auth.login_required
def get_user(id):
	pattern = re.compile('[1-9a-fA-F]{24}')
	if pattern.match(id) is None:
		return "illegal state"
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
@api.route('/users/login/', methods=['POST'])
def login_app():
	username = request.json.get('username')
	password = request.json.get('password')
	if username is None or password is None:
	 	abort(400)#missing arguments
	if User.objects(username=username).first() is None:
	 	abort(404)#user doesn't exist
	if verify_password(username, password) is False:
		abort(400)#wrong password
	id = User.objects(username=username).first().id
	return jsonify({'username': username, 'id': str(id)}), 201	

@api.route('/users/reset', methods=['POST'])
@auth.login_required
def profile_resetting():
	username = request.json.get('username')
	password = request.json.get('password')
	user = g.current_user
	if username is not None:
		user.update(username = username);
	if password is not None:
		user.reset_up_password(password);
	return jsonify({'username': username, 'pw_hash': g.current_user.password_hash}), 201

# logout
#we don't need logout, because in API Restful, we don't really create logout

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
# # modify
# #gestion de token

#fitbit
@api.route('/users/fitbit/auth/')
@auth.login_required
def request_fibit_auth():
 	head_url = "https://www.fitbit.com/oauth2/authorize?"
 	response_type = "code"
 	#redirect_uri = "http%3A%2F%2Fsleeptight2016.herokuapp.com%2F"
	state = str(g.current_user.id)
	return redirect(head_url+"response_type="+response_type+"&client_id="+client_id+"&redirect_uri="+redirect_uri+"&scope="+scope+"&expires_in="+expires_in+"&state="+state)



@api.route('/users/fitbit/callback/')
def callback_fitbit_auth():
	#collecte state and code in url
	state_id = request.args.get("state")
	#controle de state_id
	pattern = re.compile('[0-9a-fA-F]{24}')
	if pattern.match(state_id) is None:
		return "illegal state"
	user = User.objects(id=ObjectId(state_id)).first()
	code = request.args.get("code")
 	user.set_up_variable(fitbit_callback_code = code)
	#return jsonify({'code': user.fitbit_callback_code}), 200
	#request
	request_body = "client_id="+client_id+"&redirect_uri="+redirect_uri+"&grant_type=authorization_code&code="+code
	#request_body = "clientId=22zMTX&grant_type=authorization_code&redirect_uri=http%3A%2F%2Fsleeptight2016.herokuapp.com%2F&code="+code
	request_headers = {'Authorization':'Basic '+base64.b64encode(client_id+":"+client_secret), 'Content-type':'application/x-www-form-urlencoded' }
	response_curl = requests.post("https://api.fitbit.com/oauth2/token", data=request_body, headers=request_headers)
	if response_curl.status_code != 200:
 		return jsonify({'state_id': state_id, 'code':code, 'status_code':response_curl.status_code, 'text':response_curl.text})
 	#traitemetn de reponse
	response_dictionary = json.loads(response_curl.text)
	access_token = response_dictionary["access_token"]
	token_type = response_dictionary["token_type"]
	fitbit_user_id = response_dictionary["user_id"]
	fitbit_refresh_token = response_dictionary["refresh_token"]
	user.set_up_variable(fitbit_access_token=access_token, fitbit_token_type=token_type, \
		fitbit_user_id=fitbit_user_id, fitbit_refresh_token=fitbit_refresh_token)
	user.save()
	#return jsonify({'state_id': state_id, 'token_type':token_type, 'fitbit_user_id':fitbit_user_id}), 200
	return '<h1>You could go back to app SleepTight by RETURN KEY </h1>'
 	#return redirect(url_for('main.index'))

# #def refresh_token()

# #def get_access_token()
# #TODO
# @api.route('/users/fitbit/sleeps/')
# @auth.login_required
# def get_sleep_log():
# 	# verify is there sleep_log of the day
# 	user = g.current_user
# 	response_curl = requests.get("url", headers={'Authorization': user.fitbit_token_type+" "+user.fitbit_access_token}) 
# 	return response_curl.text
# 	#TODO: traitment of data
# 	#TODO: return the data to android
# 	#return jsonify()
# # generation de token fichier: authentification.py

# il faut un calcul de timeout pour les token
@api.route('/users/fitbit/sleeps/testdata/<int:year>/<int:month>/<int:day>/')
@auth.login_required
def get_sleep_log_test(year, month, day):
	user = g.current_user
	if user.fitbit_access_token is None:
		if user.fitbit_refresh_token is None:
			redirect(url_for('.request_fibit_auth'))
		fitbit_access_token, fitbit_refresh_token = refreshing_token(user.fitbit_refresh_token)
		user.set_up_variable(fitbit_access_token=fitbit_access_token)
		user.set_up_variable(fitbit_refresh_token=fitbit_refresh_token)		
	url = "https://api.fitbit.com/1/user/4KR62B/sleep/date/{}-{}-{}.json".format(year, month, day) 
	request_headers = {'Authorization':'Bearer '+user.fitbit_access_token}
 	response_curl = requests.get(url, headers=request_headers)
 	if response_curl.status_code != 200:
 		abort(response_curl.status_code)
 	response_dictionary = json.loads(response_curl.text)
 	return traitement_data_sleep(user, response_dictionary)

#refresh_token = ""
def refreshing_token(refresh_token):
 	request_body = "grant_type=refresh_token&refresh_token="+refresh_token
 	request_headers = {'Authorization':'Basic '+base64.b64encode(client_id+":"+client_secret), 'Content-type':'application/x-www-form-urlencoded' }
 	response_curl = requests.post("https://api.fitbit.com/oauth2/token", data=request_body, headers=request_headers)
 	if response_curl.status_code != 200:
 		abort(response_curl.status_code)
 	response_dictionary = json.loads(response_curl.text)
 	access_token = response_dictionary["access_token"]
 	refresh_token = response_dictionary["refresh_token"]
 	return (access_token, refresh_token)

def traitement_data_sleep(user, response_dictionary):
	sleep = response_dictionary["sleep"]
	# sleep is a list, so the next value is all wrong 9.6.2016
	sleeptestlist = []
	for singleSleep in sleep:
		awakeCount = singleSleep["awakeCount"]
		awakeningsCount = singleSleep["awakeningsCount"]
		awakeDuration = singleSleep["awakeDuration"]
		dateOfSleep = singleSleep["dateOfSleep"]
		duration = singleSleep["duration"]
		efficiency = singleSleep["efficiency"]
		isMainSleep = singleSleep["isMainSleep"]
		minutesAfterWakeup = singleSleep["minutesAfterWakeup"]
		minutesAwake = singleSleep["minutesAwake"]
		minutesAsleep = singleSleep["minutesAsleep"]
		minutesToFallAsleep = singleSleep["minutesToFallAsleep"]
		restlessCount = singleSleep["restlessCount"]
		restlessDuration =singleSleep["restlessDuration"]
		startTime = singleSleep["startTime"]
		timeInBed = singleSleep["timeInBed"]

		dateTimeStateAwake = []
		dateTimeStateReallyAwake =[]
		for logs in singleSleep["minuteData"]:
			if logs["value"] == "2":
				dateTimeStateAwake.append(logs["dateTime"])
			elif logs["value"] == "3":
				dateTimeStateReallyAwake.append(logs["dateTime"])
		#timelog = {"awakeCount":awakeCount, "awakeningsCount":awakeningsCount, "dateTimeStateAwake":dateTimeStateAwake, "dateTimeStateReallyAwake":dateTimeStateReallyAwake}
		#sleeptestlist.append(timelog)
		user.ajoute_sleep_data(awakeCount=awakeCount, awakeningsCount=awakeningsCount, \
				awakeDuration=awakeDuration, dateOfSleep=dateOfSleep, duration=duration, \
				efficiency=efficiency, isMainSleep=isMainSleep, minutesAfterWakeup=minutesAfterWakeup, \
				minutesAsleep=minutesAsleep, minutesToFallAsleep=minutesToFallAsleep, restlessCount=restlessCount, \
				restlessDuration=restlessDuration, startTime=startTime, timeInBed=timeInBed, dateTimeStateAwake=dateTimeStateAwake, \
				dateTimeStateReallyAwake=dateTimeStateReallyAwake)
	res =[]
	for sleep in user.Sleep_Data:
		res.append(sleep.to_json())
	return jsonify({'sleeptestlist':json.dumps(res)})


@api.route('/test/fitbit/get')
@auth.login_required
def get_fitbit_data():
	user = g.current_user
	res = "unset"
	dict = {'user':user.username}
	if user.fitbit_callback_code is not None:
		dict["fitbit_callback_code"] = user.fitbit_callback_code
		res = "set"
	if user.fitbit_access_token is not None:
		dict["fitbit_access_token"] = user.fitbit_access_token
		res = "set"	
	if user.fitbit_token_type is not None:
		dict["fitbit_token_type"] = user.fitbit_token_type
		res = "set"
	if user.fitbit_refresh_token is not None:
		dict["fitbit_refresh_token"] = user.fitbit_refresh_token
		res = "set"
	return jsonify(dict)

# @api.route('/test/fitbit/insert')
# @auth.login_required
# def insert_fitbit_data():
# 	user = g.current_user
# 	user.set_up_variable(fitbit_callback_code = "code")
#  	user.set_up_variable(fitbit_access_token="access_token")
#  	user.set_up_variable(fitbit_token_type="token_type")
#  	user.set_up_variable(fitbit_user_id="fitbit_user_id")
#  	user.set_up_variable(fitbit_refresh_token="fitbit_refresh_token")
# 	return jsonify({"user":user.username}), 200

