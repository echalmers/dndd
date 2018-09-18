from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=50, unique=True,
                            help_text='Using an existing name will overwrite that entry. <br> Using a new name will create a new entry <br>')
    level = models.IntegerField()
    ac = models.IntegerField()
    initiative = models.IntegerField()
