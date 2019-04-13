from django.conf.urls import url
from django.urls import path
from . import views, softViews

urlpatterns = [
    url(r'^deployinstance/$', views.main, name='main'),
    url(r'^$', views.home, name='home'),
    url(r'^login/$', views.login, name='login'),
    url(r'^launchInstance/', views.launchInstance, name='launchInstance'),
    url(r'details/', views.details,name='details'),
    url(r'^swtemplate/newapp/', softViews.swtemplate, name='swtemplate'),
    url(r'^swtemplate/myapp/', softViews.swtemplatemy, name='swtemplate2'),
    # url(r'^test/', softViews.test, name='swtemplate3'),
    path('installsoft/<softId>/<instanceId>/', softViews.installSoft, name='installSoft'),
    url(r'^deployapp/', views.deployapp, name='deployapp'),
    url(r'^buildAndDeploy/', views.buildAndDeploy, name='buildAndDeploy'),
    url(r'^createAndAssociatefp/', views.createAndAssociatefp, name='createAndAssociatefp'),
    url(r'createAndAssociatefpIns', views.createAndAssociatefpIns, name='createAndAssociatefpIns'),
    path('ilogs/<instanceId>/', views.showLogs, name='showLogs'),
    path('grablogs/<instanceId>/', views.grabLogs, name='grabLogs')
]
