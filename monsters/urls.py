from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.browse, name='browse'),
    url(r'^browse$', views.browse, name='browse'),
    url(r'^custom$', views.custom, name='custom'),
    url(r'^scrape$', views.scrape, name='scrape'),
]