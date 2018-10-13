from django.forms import ModelForm
from .models import Player


class PlayerForm(ModelForm):

    class Meta:
        model = Player
        fields = ['name',
                  'level',
                  'ac',
                  'initiative',
                  'advantage_on_init',
                  ]
        labels = {'advantage_on_init': 'Advantage on Initiative Rolls',
                  'initiative': 'Initiative Modifier'}
