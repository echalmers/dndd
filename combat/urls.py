from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.setup, name='setup_encounter'),
    url(r'^setup', views.setup, name='setup_encounter'),
    url(r'^add_pc', views.add_pc, name='add_pc'),
]