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

USER_CAN_DELETE_SKILL_SCORE = 50
USER_CAN_EDIT_SKILL_SCORE = 50

class EditSkillForm(forms.Form):
    name = forms.CharField(max_length=25)
    description = forms.CharField(max_length=200, widget=forms.Textarea)

class CreateSkillForm(EditSkillForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        if Skill.objects.filter(name=name).exists():
            self._errors['name'] = self.error_class(['Skill with this name already exists'])
        return self.cleaned_data

@login_required
def skill_create(request):
    if request.method == 'GET':
        return render(request, 'createskill.html', { 'form': CreateSkillForm(), 'submit_to': '/skills/create/' })
    if request.method == 'POST':
        form = CreateSkillForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            time = timezone.now()
            Skill.objects.create(
                    user=request.user,
                    last_updated_user=request.user,
                    name=name,
                    description=description,
                    update_date=time,
                    creation_date=time)
            return HttpResponseRedirect('/skills/')
        else:
            return render(request, 'createskill.html', { "form": form, 'submit_to': '/skills/create/'} )

@login_required
def skill_delete(request, skill_id):
    skill= Skill.objects.get(id=skill_id)
    if skill.user == request.user or request.user.score() >= USER_CAN_DELETE_SKILL_SCORE:
        skill.delete()
        return HttpResponseRedirect('/skills/')
    else:
        return HttpResponseRedirect('/skills/'+skill.url+'?err=failed_delete')

def skill_edit(request, skill_id):
    skill = Skill.objects.get(id=skill_id);
    # TODO add redirect
    if skill.user == request.user or request.user.score() >= USER_CAN_EDIT_SKILL_SCORE:
        if request.method == 'GET':
            init = {};
            init['name'] = skill.name
            init['description'] = skill.description
            form = EditSkillForm(init);
            return render(request, 'createskill.html', { "form": form, 'submit_to': skill_id+'/edit'} )
        if request.method == 'POST':
            form = EditSkillForm(request.POST)
            if form.is_valid():
                skill = Skill.objects.get(id=skill_id)
                skill.name = form.cleaned_data['name']
                skill.description = form.cleaned_data['description']
                skill.update_date = timezone.now()
                skill.save()
                return HttpResponseRedirect('/skills/')
            else:
                return render(request, 'createskill.html', { "form": form, 'submit_to': 'create'} )

def skill_list(request):
    skills = Skill.objects.order_by('-creation_date')[:10]
    context = { 'skills': skills }
    return render(request, 'skills.html', context)

def skill_search(request):
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
