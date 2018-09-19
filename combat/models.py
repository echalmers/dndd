from django.db import models
from monsters.models import Monster
from players.models import Player

class PcCombatant(models.Model):
    display_name = models.CharField(max_length=50)
    player = models.ForeignKey(Player, on_delete=None)

class NpcCombatant(models.Model):
    display_name = models.CharField(max_length=50)
    monster = models.ForeignKey(Monster, on_delete=None)




