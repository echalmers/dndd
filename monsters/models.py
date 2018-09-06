from django.db import models


class Monster(models.Model):
    name = models.CharField(max_length=50, unique=True)
    size = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    alignment = models.CharField(max_length=20)
    ac = models.IntegerField()
    hp = models.CharField(max_length=12)
    speed = models.TextField()
    str_mod = models.IntegerField()
    dex_mod = models.IntegerField()
    con_mod = models.IntegerField()
    int_mod = models.IntegerField()
    wis_mod = models.IntegerField()
    cha_mod = models.IntegerField()
    saving_throws = models.TextField(null=True)
    skills = models.TextField(null=True)
    vulnerabilies = models.TextField(null=True)
    resistances = models.TextField(null=True)
    immunities = models.TextField(null=True)
    senses = models.TextField(null=True)
    languages = models.TextField(null=True)
    cr = models.IntegerField()
    xp = models.IntegerField()
    legendary_action_notes = models.TextField(null=True)


class Trait(models.Model):
    monster = models.ForeignKey(Monster, on_delete=None)
    name = models.CharField(max_length=20)
    description = models.TextField()


class Action(models.Model):
    monster = models.ForeignKey(Monster, on_delete=None)
    name = models.CharField(max_length=20)
    description = models.TextField()


class LegendaryAction(models.Model):
    monster = models.ForeignKey(Monster, on_delete=None)
    name = models.CharField(max_length=20)
    description = models.TextField()