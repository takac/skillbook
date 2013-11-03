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

from voting.models import Vote

from skillbook.models import Skill, Resource, ScoreConst

logger = logging.getLogger(__name__)

def index(request):
    skills = Skill.objects.order_by('creation_date')[:5]
    context = { 'skills': skills }
    return render(request, 'home.html', context)

def logout_view(request):
    return logout(request)

@login_required
def vote(request, resource_id):
    direction = request.GET.get('v', '')
    skill_id = request.GET.get('skill', '')
    resource = Resource.objects.get(id=resource_id)
    vote = Vote.objects.get_for_user(resource, request.user)

    if direction == 'none':
        if vote:
            vote.delete()
    if direction == 'up':
        if vote:
            vote.vote = 1
            vote.save()
        else:
            Vote.objects.record_vote(resource, request.user, 1)
    if direction == 'down':
        if vote:
            vote.vote = -1
            vote.save()
        else:
            Vote.objects.record_vote(resource, request.user, -1)
    if skill_id:
        return HttpResponseRedirect('/skills/'+skill_id)
    else:
        return HttpResponseRedirect('/resources')

def user_profile(request):
    return render(request, 'account.html', None)

def users_list(request):
    users = User.objects.all()
    context = { 'users': users }
    return render(request, 'userlist.html', context)

def users(request, username):
    try:
        view_user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404

    resources = view_user.resource_set.all()
    skills = view_user.skill_set.all()
    context = { 'resources': resources, 'skills': skills, 'view_user': view_user, 'score_const': ScoreConst()}
    return render(request, 'users.html', context)

def activity_redirect(request):
        return HttpResponseRedirect('/account/activity')

@login_required
def activity(request):
    resources = request.user.resource_set.all()
    skills = request.user.skill_set.all()
    context = { 'resources': resources, 'skills': skills, 'view_user': request.user, 'score_const': ScoreConst()}
    return render(request, 'users.html', context)

class CreateUserForm(forms.Form):
    username = forms.CharField(max_length=25)
    password = forms.CharField(max_length=40, widget=forms.PasswordInput())
    email = forms.EmailField()

def adduser(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/?status=auth')
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            User.objects.create_user(username=username,
                    password=password,
                    email=form.cleaned_data['email'])
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect('/?status=success') # redirect to success
        else:
            return render(request, 'createuser.html', { "form": form } )

    form = CreateUserForm()
    return render(request, 'createuser.html', { "form": form } )

