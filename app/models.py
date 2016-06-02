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
	Hear_Rates = db.ListField(db.EmbeddedDocumentField('HeartRate'))
	Optional_Sleep_Data = db.EmbeddedDocumentField('SleepData')

#TODO !
#a definir selon le api de fitbit
class HeartRate(db.EmbeddedDocument):
	time = db.DateTimeField(required=True)
	value = db.IntField

class SleepData(db.EmbeddedDocument):
	Sleep_Time_Series = db.DynamicField(required = True)
	Sleep_Log = db.DynamicField(required = True)

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
	username = db.StringField(required = True, unique=True)
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
	# @property
	# def password(self):
	# 	return self.password_hash
		#raise AttributeError('password is not a readable attribute')

	def set_up_password(self, password):
		self.password_hash = generate_password_hash(password)

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
