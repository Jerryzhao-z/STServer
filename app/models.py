from . import db
import datetime
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
	name = db.StringField(required = True)
	email = db.EmailField(required = True)
	password_hash = db.StringField(required = True)
	token = db.StringField()
	Evenements = db.ListField(db.EmbeddedDocumentField('Evenement'))
	Personal_Parameters = db.EmbeddedDocumentField('Parameters')
	Friends = db.ListField(db.ReferenceField('User'))
	VoiceSent = db.ListField(db.ReferenceField('Voice'))
	Voicereceived = db.ListField(db.ReferenceField('Voice'))
