from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=50)
    ac = models.IntegerField()
    init_mod = models.IntegerField()
