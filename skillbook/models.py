from django.db import models
from django.contrib.auth.models import User
from django.contrib import auth

def user_url(self):
	return self.username

auth.models.User.add_to_class('url', user_url)

class Skill(models.Model):
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=200)
	user = models.ForeignKey(User)
	creation_date = models.DateTimeField('date created')

	def url(self): return self.id
	def __unicode__(self):
		return self.name

class Resource(models.Model):
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=200)
	link = models.CharField(max_length=100)
	skill = models.ForeignKey(Skill)
	user = models.ForeignKey(User)
	creation_date = models.DateTimeField('date created')

	def url(self): return self.id
	def vote_sum(self):
		down = Vote.objects.filter(direction=False, resource=self).count()
		up = Vote.objects.filter(direction=True, resource=self).count()
		return (up - down)

	def __unicode__(self):
		return self.name

class Vote(models.Model):
	resource = models.ForeignKey(Resource)
	user = models.ForeignKey(User)
	direction = models.BooleanField()

	def url(self): return self.id
	def __unicode__(self):
		return self.user.username + ' : ' + self.resource.name
