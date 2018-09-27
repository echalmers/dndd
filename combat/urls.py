from django.conf.urls import url
from . import views
from django.urls import path

urlpatterns = [
    url(r'^$', views.setup, name='setup_encounter'),
    url(r'^setup', views.setup, name='setup_encounter'),
    url(r'^add_pc', views.add_pc, name='add_pc'),
    path(r'remove_pc/<str:pc_name>', views.remove_pc, name='remove_pc'),
    url(r'^add_npc', views.add_npc, name='add_npc'),
    path(r'remove_npc/<str:npc_name>', views.remove_npc, name='remove_npc'),
    url(r'^randomize', views.randomize, name='random_encounter'),
    url(r'^dashboard', views.dashboard, name='combat_dashboard'),
    url(r'^advance', views.advance, name='advance_combat'),
    url(r'^change_hp', views.change_hp, name='change_hp'),
    url(r'^reset', views.reset, name='reset'),
]
