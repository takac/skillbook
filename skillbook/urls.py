from django.conf.urls import patterns, include, url
from skillbook import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'skillbook.views.home', name='home'),
    # url(r'^skillbook/', include('skillbook.foo.urls')),
	url(r'^$', views.index, name='index'),

	url(r'^resources/create/$', views.resource_create, name='create resource'),
	url(r'^resources/(?P<resource_id>\d+)/vote/$', views.vote, name='vote'),
	url(r'^resources/(?P<resource_id>\d+)/edit/$', views.resource_edit, name='edit resource'),
	url(r'^resources/(?P<resource_id>\d+)/delete/$', views.resource_delete, name='delete resource'),
	url(r'^resources/(?P<resource_id>\d+)/$', views.resource, name='resource'),
	url(r'^resources/json/$', views.resources_json, name='resources_json'),
	url(r'^resources/$', views.resources_list, name='resources_list'),

    url(r'^skills/$', views.skill_list, name='skill_list'),
	url(r'^skills/(?P<skill_id>\d+)/$', views.skill, name='skill'),
	url(r'^skills/(?P<skill_id>\d+)/edit/$', views.skill_edit, name='skill edit'),
	url(r'^skills/(?P<skill_id>\d+)/delete/$', views.skill_delete, name='skill edit'),
	url(r'^skills/create/$', views.skill_create, name='create skill'),
    url(r'^skills/json/$', views.skills_json, name='skills_json'),
    url(r'^skills/search/$', views.skill_search, name='skill search'),

	url(r'^users/(?P<username>\w+)/$', views.users, name='users'),
	url(r'^users/$', views.users_list, name='users_list'),

	(r'^account/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
	(r'^account/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/account/login'}),
	url(r'^account/activity/$', views.activity, name='user activity'),
	url(r'^account/$', views.activity_redirect, name='user activity'),
	url(r'^account/profile/$', views.user_profile, name='user_profile'),
	url(r'^account/create/$', views.adduser, name='create user'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:

	url(r'^admin/', include(admin.site.urls))
)
