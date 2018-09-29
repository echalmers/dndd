from django.db import models
from monsters.models import Monster
from players.models import Player

class PcCombatant(models.Model):
    display_name = models.CharField(max_length=50, unique=True)
    initiative = models.IntegerField()
    player = models.ForeignKey(Player, on_delete=None)

class NpcCombatant(models.Model):
    discovered_ac_max = models.IntegerField(null=True)
    discovered_ac_min = models.IntegerField(null=True)
    display_name = models.CharField(max_length=50, unique=True)
    initiative = models.IntegerField()
    max_hp = models.IntegerField()
    current_hp = models.IntegerField()
    monster = models.ForeignKey(Monster, on_delete=None)

class Combat(models.Model):
    name = models.CharField(max_length=50)
    round = models.IntegerField(default=1)
    turn = models.IntegerField(default=1)


