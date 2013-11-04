from django.conf.urls import patterns, include, url

from skillbook.views import general, resources, skills

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

	url(r'^$', general.index, name='index'),
    (r'^grappelli/', include('grappelli.urls')), # grappelli URLS
	(r'^admin/', include(admin.site.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	url(r'^resources/(?P<resource_id>\d+)/vote/$'   , resources.vote            , name='vote')            ,
	url(r'^resources/(?P<resource_id>\d+)/edit/$'   , resources.resource_edit   , name='edit resource')   ,
	url(r'^resources/(?P<resource_id>\d+)/delete/$' , resources.resource_delete , name='delete resource') ,
	url(r'^resources/(?P<resource_id>\d+)/$'        , resources.resource        , name='resource')        ,
	url(r'^resources/json/$'                        , resources.resources_json  , name='resources_json')  ,
	url(r'^resources/$'                             , resources.resources_list  , name='resources_list')  ,

	url(r'^skills/(?P<skill_id>\d+)/newresource/$' , resources.resource_create, name='resource edit')   ,
    url(r'^skills/$'                          , skills.skill_list   , name='skill_list')   ,
	url(r'^skills/(?P<skill_id>\d+)/$'        , skills.skill        , name='skill')        ,
	url(r'^skills/(?P<skill_id>\d+)/edit/$'   , skills.skill_edit   , name='skill edit')   ,
	url(r'^skills/(?P<skill_id>\d+)/delete/$' , skills.skill_delete , name='skill edit')   ,
	url(r'^skills/create/$'                   , skills.skill_create , name='create skill') ,
    url(r'^skills/json/$'                     , skills.skills_json  , name='skills_json')  ,
    url(r'^skills/search/$'                   , skills.skill_search , name='skill search') ,

	url(r'^users/(?P<username>\w+)/$' , general.users              , name='users')                    ,
	url(r'^users/$'                   , general.users_list         , name='users_list')               ,
	url(r'^account/activity/$'        , general.activity           , name='user activity')            ,
	url(r'^account/$'                 , general.activity_redirect  , name='user activity')            ,
	url(r'^account/profile/$'         , general.user_profile       , name='user_profile')             ,
	url(r'^account/create/$'          , general.adduser            , name='create user')              ,

	(r'^account/login/$'              , 'django.contrib.auth.views.login'  , {'template_name': 'login.html'}) ,
	(r'^account/logout/$'             , 'django.contrib.auth.views.logout' , {'next_page': '/account/login'}) ,
)
