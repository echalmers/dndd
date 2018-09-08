from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.browse, name='browse'),
    url(r'^browse$', views.browse, name='browse'),
    url(r'^scrape$', views.scrape, name='scrape'),
    url(r'^create$', views.create, name='create'),
]