from django.http import HttpResponse, HttpResponseRedirect, Http404
from django import forms
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from skillbook.models import Skill, Resource, Vote

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
            vote.save()
        else:
            Vote.objects.create(user=request.user, resource=resource, direction=True)
    if direction == 'down':
        if vote:
            vote.direction = False
            vote.save()
        else:
            Vote.objects.create(user=request.user, resource=resource, direction=False)
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
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404

    resources = user.resource_set.all()
    skills = user.skill_set.all()
    context = { 'resources': resources, 'skills': skills }
    return render(request, 'users.html', context)

@login_required
def activity(request):
    resources = request.user.resource_set.all()
    skills = request.user.skill_set.all()
    context = { 'resources': resources, 'skills': skills }
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
        return render(request, 'createskill.html', { 'form': CreateSkillForm() })
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
            return render(request, 'createskill.html', { "form": form } )

def skills_list(request):
    skills = Skill.objects.order_by('creation_date')[:10]
    context = { 'skills': skills }
    return render(request, 'skills.html', context)

def skill(request, skill_id):
    skill = Skill.objects.get(id=skill_id)
    resources = skill.resource_set.all()
    o = []
    for r in resources:
        d = {'resource': r}
        if request.user.is_authenticated():
            try:
                v = Vote.objects.get(user=request.user, resource=r)
                d['vote'] = v
            except Vote.DoesNotExist:
                pass
        o.append(d)
    context = { 'skill': skill, 'resources': resources, 'comp': o}
    return render(request, 'skill.html', context)

def resource(request, resource_id):
    return HttpResponse("Looking at resource %s" % resource_id)

def resources_list(request):
    resources = Resource.objects.order_by('creation_date')[:10]
    context = { 'resources': resources }
    return render(request, 'resources.html', context)

class CreateResourceForm(forms.Form):
    name = forms.CharField(max_length=40)
    link = forms.CharField(max_length=200)
    description = forms.CharField(max_length=200, widget=forms.Textarea)
    skill = forms.ModelChoiceField(queryset=Skill.objects.all())

def resource_create(request):
    if request.method == 'GET':
        initial = {}
        if request.GET.get('skill', ''):
            try:
                initial['skill'] = Skill.objects.get(name=request.GET.get('skill',''))
            except Skill.DoesNotExist:
                pass

        form = CreateResourceForm(initial=initial)
        return render(request, 'createresource.html', { 'form': form })
    if request.method == 'POST':
        form = CreateResourceForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            link = form.cleaned_data['link']
            skill = form.cleaned_data['skill']
            time = timezone.now()
            Resource.objects.create(user=request.user,
                    name=name, description=description,creation_date=time, link=link,skill=skill)
            return HttpResponseRedirect('/skills/')
        else:
            return render(request, 'createresource.html', { "form": form } )



