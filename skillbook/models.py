from django.db import models
from django.contrib.auth.models import User
from django.contrib import auth

def user_url(self):
	return self.username

def user_score(self):
	score = 0
	# combine vote score
	for i in self.resource_set.all():
		score += i.vote_sum()
	# 4 for adding a resource
	score += self.resource_set.count() * 4
	# 3 for adding skill
	score += self.skill_set.count() * 3
	return score

auth.models.User.add_to_class('url', user_url)
auth.models.User.add_to_class('score', user_score)

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

class Review(models.Model):
	resource = models.ForeignKey(Resource)
	user = models.ForeignKey(User)
	creation_date = models.DateTimeField('date created')
	content = models.CharField(max_length=10000)
	title = models.CharField(max_length=40)

	def __unicode__(self):
		return title

class ReviewComment(models.Model):
	review = models.ForeignKey(Review)
	user = models.ForeignKey(User)
	creation_date = models.DateTimeField('date created')
	content = models.CharField(max_length=5000)

