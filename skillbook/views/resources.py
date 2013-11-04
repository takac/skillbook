import json
import logging
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db.models import Sum, Avg
from django import forms
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.core import serializers

from voting.models import Vote

from skillbook.models import Skill, Resource, ScoreConst

logger = logging.getLogger(__name__)

USER_CAN_DELETE_RESOURCE_SCORE = 30
USER_CAN_EDIT_RESOURCE_SCORE = 30

def resource(request, resource_id):
    return render(request, 'resource.html', { 'resource': Resource.objects.get(id=resource_id)})

def resources_list(request):
    resources = Resource.objects.order_by('-creation_date')
    context = { 'resources': resources }
    return render(request, 'resources.html', context)

@login_required
def vote(request, resource_id):
    direction = request.GET.get('v', '')
    skill_id = request.GET.get('skill', '')
    resource = Resource.objects.get(id=resource_id)
    vote = Vote.objects.get_for_user(resource, request.user)

    if direction == 'none':
        if vote:
            vote.delete()
    elif direction == 'up':
        if vote:
            vote.vote = 1
            vote.save()
        else:
            Vote.objects.record_vote(resource, request.user, 1)
    elif direction == 'down':
        if vote:
            vote.vote = -1
            vote.save()
        else:
            Vote.objects.record_vote(resource, request.user, -1)

    if skill_id:
        return HttpResponseRedirect('/skills/'+skill_id)
    else:
        return HttpResponseRedirect('/resources')

def resources_json(request):
    term = None
    query = None
    if request.method == 'GET':
        term = request.GET.get('term', '')
    if request.method == 'POST':
        term = request.POST.get('term', '')
    if term:
        query = Resource.objects.filter(name__contains=term)
    else:
        query = Resource.objects.all()
    
    data = serializers.serialize("json", query)

    return HttpResponse(data, content_type="application/json")

class EditResourceForm(forms.Form):
    name = forms.CharField(max_length=40)
    link = forms.CharField(max_length=200)
    description = forms.CharField(max_length=500, widget=forms.Textarea)
    # skill = forms.ModelChoiceField(queryset=Skill.objects.all())

class CreateResourceForm(EditResourceForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        skill = self.cleaned_data.get('skill')
        if Resource.objects.filter(name=name, skill=skill).exists():
            self._errors['name'] = self.error_class(['A resource with this name already exists for '+skill.name])
        return self.cleaned_data

@login_required
def resource_delete(request, resource_id):
    resource = Resource.objects.get(id=resource_id)
    if resource.user == request.user or request.user.score() >= USER_CAN_DELETE_RESOURCE_SCORE:
        resource.delete()
        return HttpResponseRedirect('/skills/'+str(resource.skill.id))
    else:
        return HttpResponseRedirect('/skills/?delete=failed')

@login_required
def resource_edit(request, resource_id):
    # TODO add redirect
    resource = Resource.objects.get(id=resource_id)
    if resource.user == request.user or request.user.score() >= USER_CAN_EDIT_RESOURCE_SCORE:
        if request.method == 'GET':
            init = {}
            init['name'] = resource.name
            init['description'] = resource.description
            init['link'] = resource.link
            form = EditResourceForm(init)
            return render(request, 'createresource.html', { 'form': form, 'submit_to': '/resources/'+resource_id+'/edit/' })
        if request.method == 'POST':
            form = EditResourceForm(request.POST)
            if form.is_valid():
                resource = Resource.objects.get(id=resource_id)
                resource.name = form.cleaned_data['name']
                resource.description = form.cleaned_data['description']
                resource.link = form.cleaned_data['link']
                resource.update_date = timezone.now()
                resource.save()
                return HttpResponseRedirect('/resources/'+str(resource.id)+'/')
            else:
                return render(request, 'createresource.html', { "form": form, 'submit_to': resource_id + '/edit' } )

def resource_create(request, skill_id):
    if request.method == 'GET':
        initial = {}
        initial['skill'] = Skill.objects.get(id=skill_id)
        form = CreateResourceForm(initial=initial)
        return render(request, 'createresource.html', { 'form': form, 'submit_to': '/skills/'+str(skill_id)+'/newresource/'})
    if request.method == 'POST':
        form = CreateResourceForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            link = form.cleaned_data['link']
            skill = Skill.objects.get(id=skill_id)
            time = timezone.now()
            resouce = Resource.objects.create(
                    user=request.user,
                    last_updated_user=request.user,
                    score=0,
                    name=name,
                    description=description,
                    update_date=time,
                    creation_date=time,
                    link=link,
                    skill=skill)

            return HttpResponseRedirect('/skills/' + str(resouce.skill.id) + '/')
        else:
            return render(request, 'createresource.html', { "form": form, 'submit_to': 'create'} )


