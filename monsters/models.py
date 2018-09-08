from django.db import models


class Monster(models.Model):
    name = models.CharField(max_length=50, unique=True)
    size = models.CharField(max_length=20, null=True)
    type = models.CharField(max_length=20, null=True)
    alignment = models.CharField(max_length=20, null=True)
    ac = models.IntegerField(null=True)
    hp = models.CharField(max_length=12, null=True)
    speed = models.TextField(null=True)
    str_mod = models.IntegerField(null=True)
    dex_mod = models.IntegerField(null=True)
    con_mod = models.IntegerField(null=True)
    int_mod = models.IntegerField(null=True)
    wis_mod = models.IntegerField(null=True)
    cha_mod = models.IntegerField(null=True)
    saving_throws = models.TextField(null=True)
    skills = models.TextField(null=True)
    vulnerabilies = models.TextField(null=True)
    resistances = models.TextField(null=True)
    immunities = models.TextField(null=True)
    senses = models.TextField(null=True)
    languages = models.TextField(null=True)
    cr = models.FloatField(null=True)
    xp = models.IntegerField(null=True)
    traits = models.TextField(null=True)
    actions = models.TextField(null=True)
    legendary_actions = models.TextField(null=True)
