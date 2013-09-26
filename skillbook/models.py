from re import sub
from django.db import models
from django.db.models import Sum, Avg
from django.contrib.auth.models import User
from django.contrib import auth

from voting.models import Vote

class ScoreConst():
	create_resource_score = 5
	create_skill_score = 2

def user_url(self):
	return self.username

def user_score(self):
	score = 0
	# combine vote score
	for r in self.resource_set.all():
		score += r.score
	# 4 for adding a resource
	score += self.resource_set.count() * ScoreConst.create_resource_score
	# 3 for adding skill
	score += self.skill_set.count() * ScoreConst.create_skill_score
	return score

auth.models.User.add_to_class('url', user_url)
auth.models.User.add_to_class('score', user_score)

class Skill(models.Model):
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=200)
	user = models.ForeignKey(User)
	creation_date = models.DateTimeField('date created')
	update_date = models.DateTimeField('last updated')
	last_updated_user = models.ForeignKey(User, related_name='resource_last_updated_user')

	def url(self): return self.id
	def __unicode__(self):
		return self.name

class Resource(models.Model):
	name = models.CharField(max_length=50)
	score = models.SmallIntegerField()
	description = models.CharField(max_length=200)
	link = models.CharField(max_length=100)
	skill = models.ForeignKey(Skill)
	user = models.ForeignKey(User)
	creation_date = models.DateTimeField('date created')
	update_date = models.DateTimeField('last updated')
	last_updated_user = models.ForeignKey(User, related_name='skill_last_updated_user')

	def url(self): return self.id
	def stripped_link(self):
		clean = sub('(https?)?(://)?(www.)?', '', self.link)
		return sub('/$','', clean)
	def __unicode__(self):
		return self.name

def denormalize_votes(sender, instance, created=False, **kwargs):
    instance.object.score = Vote.objects.get_score(instance.object)['score']
    instance.object.save()

models.signals.post_save.connect(denormalize_votes, sender=Vote)
models.signals.post_delete.connect(denormalize_votes, sender=Vote)


class Review(models.Model):
	resource = models.ForeignKey(Resource)
	user = models.ForeignKey(User)
	creation_date = models.DateTimeField('date created')
	update_date = models.DateTimeField('last updated')
	content = models.CharField(max_length=10000)
	title = models.CharField(max_length=40)

	def __unicode__(self):
		return title

class ReviewComment(models.Model):
	review = models.ForeignKey(Review)
	user = models.ForeignKey(User)
	creation_date = models.DateTimeField('date created')
	update_date = models.DateTimeField('last updated')
	content = models.CharField(max_length=5000)

