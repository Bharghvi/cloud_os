from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^main/$', views.main, name='main'),
    url(r'^$', views.home, name='home'),
    url(r'^login/$', views.login, name='login'),
    url(r'createinstance/', views.createInstance, name='createInstance')
]
