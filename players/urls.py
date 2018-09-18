from django.conf.urls import url
from . import views
from django.urls import path

urlpatterns = [
    url(r'^$', views.browse, name='browse'),
    url(r'^browse$', views.browse, name='browse_players'),
    url(r'^create$', views.create, name='create_player'),
    path('create/<str:name>/', views.create, name='create_player'),
    path('delete/<str:name>/', views.delete, name='delete_player'),
]