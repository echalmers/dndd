from django.db import models


class Monster(models.Model):
    name = models.CharField(max_length=50, unique=True)
    size = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    alignment = models.CharField(max_length=2)
    ac = models.IntegerField(max_length=2)
    hp = models.IntegerField(max_length=3)
    speed = models.TextField()
    str_mod = models.IntegerField()
    dex_mod = models.IntegerField()
    con_mod = models.IntegerField()
    int_mod = models.IntegerField()
    wis_mod = models.IntegerField()
    cha_mod = models.IntegerField()
    saving_throws = models.TextField()
    skills = models.TextField()
    vulnerabiliies = models.TextField()
    resistances = models.TextField()
    immunities = models.TextField()
    passive_perception = models.IntegerField()
    senses = models.TextField()
    languages = models.TextField()
    cr = models.IntegerField(max_length=2)
    xp = models.IntegerField()


class Trait(models.Model):
    monster = models.ForeignKey(Monster, on_delete=None)
    name = models.CharField(20)
    description = models.TextField()


class Action(models.Model):
    monster = models.ForeignKey(Monster, on_delete=None)
    name = models.CharField(20)
    description = models.TextField()
