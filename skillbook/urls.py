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
	url(r'^skills/(?P<skill_id>\d+)/$', views.skill, name='skill'),
	url(r'^resources/(?P<resource_id>\d+)/vote$', views.vote, name='vote'),
	url(r'^resources/(?P<resource_id>\d+)/$', views.resource, name='resource'),
	url(r'^resources$', views.resources_list, name='resources_list'),
	url(r'^skills/$', views.skills_list, name='skills_list'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:

	url(r'^admin/', include(admin.site.urls))
)