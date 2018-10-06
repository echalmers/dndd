from django.forms import ModelForm
from .models import Monster

class MonsterForm(ModelForm):

    class Meta:
        model = Monster
        fields = ['name',
                  'ac',
                  'hp',
                  'speed',
                  'strength',
                  'dexterity',
                  'constitution',
                  'intelligence',
                  'wisdom',
                  'charisma',
                  'saving_throws',
                  'traits',
                  'actions',
                  'vulnerabilies',
                  'resistances',
                  'immunities',
                  'cr',
                  'xp',
                  ]

# from django import forms
#
# class NewMonsterForm(forms.Form):
#     name = forms.CharField()
#     size = forms.CharField()
#     type = forms.CharField()
#     alignment = forms.CharField()
#     ac = forms.IntegerField(min_value=1, widget=forms.NumberInput)
#     hp = forms.CharField()
#     speed = forms.CharField()
#     str_mod = forms.IntegerField(min_value=-10, max_value=10, widget=forms.NumberInput)
#     dex_mod = forms.IntegerField(min_value=-10, max_value=10, widget=forms.NumberInput)
#     con_mod = forms.IntegerField(min_value=-10, max_value=10, widget=forms.NumberInput)
#     int_mod = forms.IntegerField(min_value=-10, max_value=10, widget=forms.NumberInput)
#     wis_mod = forms.IntegerField(min_value=-10, max_value=10, widget=forms.NumberInput)
#     cha_mod = forms.IntegerField(min_value=-10, max_value=10, widget=forms.NumberInput)
#     saving_throws = forms.CharField()
#
#     traits = forms.CharField(widget=forms.Textarea)
#     actions = forms.CharField(widget=forms.Textarea)
#     legendary_actions = forms.CharField(widget=forms.Textarea)
#
#     skills = forms.CharField()
#     vulnerabilies = forms.CharField(widget=forms.Textarea)
#     resistances = forms.CharField(widget=forms.Textarea)
#     immunities = forms.CharField(widget=forms.Textarea)
#     senses = forms.CharField()
#     languages = forms.CharField()
#     cr = forms.FloatField()
#     xp = forms.IntegerField()

