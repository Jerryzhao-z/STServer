from . import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request, url_for
import datetime
import hashlib
#TODO !
#Pour l'instant, on a seulement defini un type primaire pour les parametres
#le probleme c'est pour l'instant on ne sait pas qu'il sont les parametre necessaire.
class Parameter(db.EmbeddedDocument):
	Name = db.StringField(required = True);
	Value = db.IntField();

class Parameters(db.EmbeddedDocument):
	Sleep_Habit = db.ListField(db.EmbeddedDocumentField('Parameter'))

# tous les evenement sont sous cette forme, de plus, on a prevu un option pour Sleep data
class Evenement(db.EmbeddedDocument):
	create_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	beginning_time = db.DateTimeField(required=True)
	Ending_time = db.DateTimeField(required=True)
	description = db.StringField(required=True)
	tag = db.ListField(field=db.StringField(max_length=140))

#TODO !
#a definir selon le api de fitbit
class HeartRate(db.EmbeddedDocument):
	time = db.DateTimeField(required=True)
	value = db.IntField()

class SleepData(db.EmbeddedDocument):
	awakeCount = db.IntField()
	awakeningsCount = db.IntField()
	awakeDuration = db.IntField()
	dateOfSleep = db.DateTimeField(required=True)
	duration = db.IntField()
	efficiency = db.IntField()
	isMainSleep = db.BooleanField()
	minutesAfterWakeup = db.IntField()
	minutesAwake = db.IntField()
	minutesAsleep = db.IntField()
	minutesToFallAsleep = db.IntField()
	restlessCount = db.IntField()
	restlessDuration = db.IntField()
	startTime = db.DateTimeField()
	timeInBed = db.IntField()
	dateTimeStateAwake = db.ListField(field=db.StringField(max_length=140))
	dateTimeStateReallyAwake =db.ListField(field=db.StringField(max_length=140))

	def set_up_variable(self, awakeCount=None, awakeningsCount=None, \
				awakeDuration=None, dateOfSleep=None, duration=None, \
				efficiency=None, isMainSleep=None, minutesAfterWakeup=None, \
				minutesAsleep=None, minutesToFallAsleep=None, restlessCount=None, \
				restlessDuration=None, startTime=None, timeInBed=None, dateTimeStateAwake=None, \
				dateTimeStateReallyAwake=None):
		if awakeCount is not None:
			self.update(awakeCount = awakeCount, upsert = True)
		if awakeningsCount is not None:
			self.update(awakeningsCount = awakeningsCount, upsert = True)
		if awakeDuration is not None:
			self.update(awakeDuration = awakeDuration, upsert = True)
		if dateOfSleep is not None:
			self.update(dateOfSleep = dateOfSleep, upsert = True)	
		if duration is not None:
			self.update(duration = duration, upsert = True)
		if efficiency is not None:
			self.update(efficiency = efficiency, upsert = True)
		if isMainSleep is not None:
			self.update(isMainSleep = isMainSleep, upsert = True)
		if minutesAfterWakeup is not None:
			self.update(minutesAfterWakeup = minutesAfterWakeup, upsert = True)
		if minutesAsleep is not None:
			self.update(minutesAsleep = minutesAsleep, upsert = True)	
		if minutesToFallAsleep is not None:
			self.update(minutesToFallAsleep = minutesToFallAsleep, upsert = True)
		if restlessCount is not None:
			self.update(restlessCount = restlessCount, upsert = True)
		if restlessDuration is not None:
			self.update(restlessDuration = restlessDuration, upsert = True)
		if startTime is not None:
			self.update(startTime = startTime, upsert = True)
		if timeInBed is not None:
			self.update(timeInBed = timeInBed, upsert = True)	
		if dateTimeStateAwake is not None:
			self.update(dateTimeStateAwake = dateTimeStateAwake, upsert = True)
		if dateTimeStateReallyAwake is not None:
			self.update(dateTimeStateReallyAwake = dateTimeStateReallyAwake, upsert = True)

	def to_json(self):
		json_sleepdata = {
			"awakeCount": self.awakeCount, 
			"awakeningsCount": self.awakeningsCount,
			"awakeDuration": self.awakeDuration, 
			"dateOfSleep": self.dateOfSleep, 
			"duration": self.duration, 
			"efficiency": self.efficiency, 
			"isMainSleep": self.isMainSleep, 
			"minutesAfterWakeup": self.minutesAfterWakeup, 
			"minutesAsleep": self.minutesAsleep, 
			"minutesToFallAsleep": self.minutesToFallAsleep,
			"restlessCount": self.restlessCount, 
			"restlessDuration": self.restlessDuration, 
			"startTime": self.startTime, 
			"timeInBed": self.timeInBed,  
			"dateTimeStateAwake": self.dateTimeStateAwake, 
			"dateTimeStateReallyAwake": self.dateTimeStateReallyAwake,  
		}
		return json_sleepdata

class Voice(db.Document):
	create_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	sender = db.ReferenceField('User')
	receiver = db.ReferenceField('User')
	voices = db.ListField(field = db.BinaryField())

# al the user log in with their email and password_hash
# token: reserve pour enregister des token de Hue(ampoule), fitbit et google 
# Evenements: liste de evenement 
# Personal_Parameters : les parameters calcule pour deduire le temps de repo
# Friends : les amis
class User(db.Document):
	username = db.StringField(required = True)
	email = db.EmailField()
	password_hash = db.StringField(required = True)
	token = db.StringField()
	Evenements = db.ListField(db.EmbeddedDocumentField('Evenement'))
	Personal_Parameters = db.EmbeddedDocumentField('Parameters')
	Friends = db.ListField(db.ReferenceField('User'))
	VoiceSent = db.ListField(db.ReferenceField('Voice'))
	Voicereceived = db.ListField(db.ReferenceField('Voice'))
	fitbit_callback_code = db.StringField()
	fitbit_access_token = db.StringField()
	fitbit_user_id = db.StringField()
	fitbit_token_type = db.StringField()
	fitbit_refresh_token = db.StringField()
	Hear_Rates = db.EmbeddedDocumentListField(HeartRate)
	Sleep_Data = db.EmbeddedDocumentListField(SleepData)

	def set_up_variable(self, fitbit_callback_code=None, fitbit_access_token=None, fitbit_user_id=None, fitbit_token_type=None, fitbit_refresh_token=None):
		if fitbit_callback_code is not None:
			self.update(fitbit_callback_code = fitbit_callback_code, upsert = True)
		if fitbit_access_token is not None:
			self.update(fitbit_access_token = fitbit_access_token, upsert = True)
		if fitbit_user_id is not None:
			self.update(fitbit_user_id = fitbit_user_id, upsert = True)
		if fitbit_token_type is not None:
			self.update(fitbit_token_type = fitbit_token_type, upsert = True)	
		if fitbit_refresh_token is not None:
			self.update(fitbit_refresh_token = fitbit_refresh_token, upsert = True)		
	# @property
	# def password(self):
	# 	return self.password_hash
		#raise AttributeError('password is not a readable attribute')

	def set_up_password(self, password):
		self.password_hash = generate_password_hash(password)

	def reset_up_password(self, password):
		self.update(password_hash = generate_password_hash(password))

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def generate_confirmation_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm': self.id})

	def confirm(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		return True

	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset': self.id})

	def reset_password(self, token, new_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('reset') != self.id:
			return False
		self.password = new_password
		db.session.add(self)
		return True

	def generate_auth_token(self, expiration):
		s = Serializer(current_app.config['SECRET_KEY'],
							expires_in=expiration)
		return s.dumps({'id': self.id}).decode('ascii')

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return None
		return User.query.get(data['id'])

	def ajoute_sleep_data(self, dateOfSleep, awakeCount=None, awakeningsCount=None, \
				awakeDuration=None, duration=None, \
				efficiency=None, isMainSleep=None, minutesAfterWakeup=None, \
				minutesAsleep=None, minutesToFallAsleep=None, restlessCount=None, \
				restlessDuration=None, startTime=None, timeInBed=None, dateTimeStateAwake=None, \
				dateTimeStateReallyAwake=None):
		singleSleep = self.Sleep_Data.create(dateOfSleep=dateOfSleep)
		singleSleep.set_up_variable(awakeCount=awakeCount, awakeningsCount=awakeningsCount, \
				awakeDuration=awakeDuration, duration=duration, \
				efficiency=efficiency, isMainSleep=isMainSleep, minutesAfterWakeup=minutesAfterWakeup, \
				minutesAsleep=minutesAsleep, minutesToFallAsleep=minutesToFallAsleep, restlessCount=restlessCount, \
				restlessDuration=restlessDuration, startTime=startTime, timeInBed=timeInBed, dateTimeStateAwake=dateTimeStateAwake, \
				dateTimeStateReallyAwake=dateTimeStateReallyAwake);
	





