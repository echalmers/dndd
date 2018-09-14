from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    url(r'^$', views.browse, name='browse_monsters'),
    url(r'^browse$', views.browse, name='browse_monsters'),
    url(r'^scrape$', views.scrape, name='scrape'),
    url(r'^create$', views.create, name='create_monster'),
    path('create/<str:name>/', views.create, name='create_monster'),
    path('delete/<str:name>/', views.delete, name='delete_monster'),
    # path('<str:name>', views.show, name="show_monster"),
    url(r'^deets', views.deets, name='deets'),
]