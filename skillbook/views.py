from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import logging

from skillbook.models import Skill, Resource, Vote

logger = logging.getLogger(__name__)

def index(request):
	skills = Skill.objects.order_by('creation_date')[:5]
	context = { 'skills': skills }
	return render(request, 'home.html', context)

@login_required
def vote(request, resource_id):
	direction = request.GET.get('v', '')
	skill_id = request.GET.get('skill', '')
	resource = Resource.objects.get(id=resource_id)
	votes = Vote.objects.filter(resource=resource, user=request.user)
	vote = None
	if votes.exists():
		vote = votes[0]

	if direction == 'none':
		if vote:
			vote.delete()
	if direction == 'up':
		if vote:
			vote.direction = True
		else:
			Vote.objects.create(user=request.user, resource=resource, direction=True)
	if direction == 'down':
		if vote:
			vote.direction = False
		else:
			Vote.objects.create(user=request.user, resource=resource, direction=False)
	if skill_id:
		return HttpResponseRedirect('/skills/'+skill_id)
	else:
		return HttpResponseRedirect('/resources')




def skills_list(request):
	skills = Skill.objects.order_by('creation_date')[:10]
	context = { 'skills': skills }
	return render(request, 'skills.html', context)

def skill(request, skill_id):
	skill = Skill.objects.get(id=skill_id)
	resources = skill.resource_set.all()
	votes = Vote.objects.filter(user=request.user)
	voted_for = [v.resource for v in Vote.objects.filter(user=request.user)]
	o = []
	for r in resources:
		d = {'resource': r}
		if r in voted_for:
			d['vote'] = [ x for x in votes if x.resource == r ][0]
		o.append(d)
	context = { 'skill': skill, 'resources': resources, 'comp': o}
	return render(request, 'skill.html', context)

def resource(request, resource_id):
	return HttpResponse("Looking at resource %s" % resource_id)

def resources_list(request):
	resources = Resource.objects.order_by('creation_date')[:10]
	context = { 'resources': resources }
	return render(request, 'resources.html', context)


