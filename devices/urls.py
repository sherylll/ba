from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^led/', views.led, name = "led"),
    url(r'^led/0', views.led, name = "led"),
    url(r'^led/1', views.led, name = "led"),
    
    url(r'^switch/$', views.switch, name = "switch"),
    
    url(r'^add/$', views.add, name='add'),
    url(r'^adduser/$', views.adduser, name='adduser'),
    
    url(r'^.*$', views.index, name='index'),
]
