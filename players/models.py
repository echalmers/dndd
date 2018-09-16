from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=50)
    level = models.IntegerField()
    ac = models.IntegerField()
    initiative = models.IntegerField()
