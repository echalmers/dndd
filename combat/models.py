from django.db import models
from monsters.models import Monster
from players.models import Player

class PcCombatant(models.Model):
    display_name = models.CharField(max_length=50, unique=True)
    initiative = models.IntegerField()
    player = models.ForeignKey(Player, on_delete=None)

class NpcCombatant(models.Model):
    display_name = models.CharField(max_length=50, unique=True)
    initiative = models.IntegerField()
    max_hp = models.IntegerField()
    current_hp = models.IntegerField()
    monster = models.ForeignKey(Monster, on_delete=None)

class CombatState(models.Model):
    round = models.IntegerField()
    turn = models.IntegerField()


