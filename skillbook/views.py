import json
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

def account(request):
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
    context = { 'resources': resources, 'skills': skills, 'view_user': view_user}
    return render(request, 'users.html', context)

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

class CreateSkillForm(forms.Form):
    name = forms.CharField(max_length=25)
    description = forms.CharField(max_length=200, widget=forms.Textarea)

@login_required
def skill_create(request):
    if request.method == 'GET':
        return render(request, 'createskill.html', { 'form': CreateSkillForm(), 'submit_to': 'create' })
    if request.method == 'POST':
        form = CreateSkillForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            time = timezone.now()
            Skill.objects.create(user=request.user,
                    name=name, description=description,creation_date=time)
            return HttpResponseRedirect('/skills/')
        else:
            return render(request, 'createskill.html', { "form": form, 'submit_to': 'create'} )

def skill_edit(request, skill_id):
    if request.method == 'GET':
        skill = Skill.objects.get(id=skill_id);
        init = {};
        init['name'] = skill.name
        init['description'] = skill.description
        form = CreateSkillForm(init);
        return render(request, 'createskill.html', { "form": form, 'submit_to': skill_id+'/edit'} )
    if request.method == 'POST':
        form = CreateSkillForm(request.POST)
        if form.is_valid():
            skill = Skill.objects.get(id=skill_id)
            skill.name = form.cleaned_data['name']
            skill.description = form.cleaned_data['description']
            skill.save()
            return HttpResponseRedirect('/skills/')
        else:
            return render(request, 'createskill.html', { "form": form, 'submit_to': 'create'} )

def skills_list(request):
    skills = Skill.objects.order_by('creation_date')[:10]
    context = { 'skills': skills }
    return render(request, 'skills.html', context)

def skills_search(request):
    return render(request, 'autocomplete.html', {})

def skills_json(request):
    term = request.GET.get('term', '')
    skills = Skill.objects.order_by('creation_date')
    if term:
        skills = [skill for skill in skills if term.lower() in skill.name.lower()]
    d = {}
    for i in skills:
        xd = {}
        xd['name'] = i.name
        xd['id'] = i.id
        xd['creation_date'] = i.creation_date.strftime("%H:%M:%S %d/%m/%Y")
        d[i.id] = xd

    return HttpResponse(json.dumps(d), content_type="application/json")

def skill(request, skill_id):
    skill = Skill.objects.get(id=skill_id)
    resources = skill.resource_set.all().order_by('-score')

    o = []
    for r in resources:
        d = {'resource': r}
        if request.user.is_authenticated():
            try:
                d['vote'] = Vote.objects.get_for_user(r, request.user)
            except Vote.DoesNotExist:
                pass
        o.append(d)
    context = { 'skill': skill, 'resources': resources, 'comp': o}
    return render(request, 'skill.html', context)

def resource(request, resource_id):
    return render(request, 'resource.html', { 'resource': Resource.objects.get(id=resource_id)})

def resources_list(request):
    resources = Resource.objects.order_by('creation_date')
    context = { 'resources': resources }
    return render(request, 'resources.html', context)

def resources_json(request):
    resources = Resource.objects.order_by('creation_date')
    return HttpResponse(json.dumps(resources), content_type="application/json")

class CreateResourceForm(forms.Form):
    name = forms.CharField(max_length=40)
    link = forms.CharField(max_length=200)
    description = forms.CharField(max_length=200, widget=forms.Textarea)
    skill = forms.ModelChoiceField(queryset=Skill.objects.all())

def resource_edit(request, resource_id):
    if request.method == 'GET':
        resource = Resource.objects.get(id=resource_id)
        init = {}
        init['name'] = resource.name
        init['description'] = resource.description
        init['link'] = resource.link
        init['skill'] = resource.skill.id
        form = CreateResourceForm(init)
        return render(request, 'createresource.html', { 'form': form, 'submit_to': resource_id+'/edit' })
    if request.method == 'POST':
        form = CreateResourceForm(request.POST)
        if form.is_valid():
            resource = Resource.objects.get(id=resource_id)
            resource.name = form.cleaned_data['name']
            resource.description = form.cleaned_data['description']
            resource.link = form.cleaned_data['link']
            resource.skill = form.cleaned_data['skill']
            resource.save()
            return HttpResponseRedirect('/skills/'+str(resource.skill.id)+'/')
        else:
            return render(request, 'createresource.html', { "form": form } )


def resource_create(request):
    if request.method == 'GET':
        initial = {}
        if request.GET.get('skill', ''):
            try:
                initial['skill'] = Skill.objects.get(name=request.GET.get('skill',''))
            except Skill.DoesNotExist:
                pass

        form = CreateResourceForm(initial=initial)
        return render(request, 'createresource.html', { 'form': form, 'submit_to': 'create'})
    if request.method == 'POST':
        form = CreateResourceForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            link = form.cleaned_data['link']
            skill = form.cleaned_data['skill']
            time = timezone.now()
            resouce = Resource.objects.create(user=request.user,
                    name=name, description=description,creation_date=time, link=link,skill=skill)
            return HttpResponseRedirect('/skills/'+resouce.skill.id+'/')
        else:
            return render(request, 'createresource.html', { "form": form } )



