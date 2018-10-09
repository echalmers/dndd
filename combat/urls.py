from django.conf.urls import url
from . import views
from django.urls import path

urlpatterns = [
    url(r'^$', views.player_view, name='player_view'),
    url(r'^browse', views.browse, name='combat_list'),
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
    url(r'^player_view$', views.player_view, name='player_view'),
    url(r'^player_view_table', views.player_view_table, name='player_view_table'),
    path(r'set_combat/<str:name>', views.set_active_combat, name='set_combat'),
    path(r'delete_combat/<str:name>', views.delete_combat, name='delete_combat'),
    url(r'^create', views.create_combat, name='create_combat'),

]
