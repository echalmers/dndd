from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from util import df_to_text
import pandas as pd
from monsters.models import Monster
from .forms import MonsterForm
from django.urls import reverse
from django.forms.models import model_to_dict
from roller.views import rolls2links, signed_string
import traceback
import json


def browse(request):
    m = Monster.objects.all().values()
    df = pd.DataFrame.from_records(m)
    df = df[['name', 'type', 'hp', 'ac', 'speed', 'cr', 'xp']]
    df = df.sort_values(['cr', 'name'])

    df['actions'] = '<a href="create/' + df['name'] \
                    + '">clone/edit</a>   <a href="delete/' + df['name'] \
                    + '">delete</a>'

    df['name'] = df['name'].apply(lambda x: '<a onclick="loadDescript(\'{name}\')" href="#">{name}</a>'.format(name=x))

    variables = df_to_text(df, 'monster')

    return render(request, 'monsters/browse.html', variables)

def custom(request):
    return render(request, 'monsters/create.html' )

def scrape(request):
    return render(request, 'monsters/scrape.html' )

def delete(request, name):
    Monster.objects.get(name=name).delete()
    return HttpResponseRedirect(reverse('browse_monsters'))

def create(request, name=None):

    print(request)
    print(name)

    if request.method == 'POST':
        if name is not None:
            m = Monster.objects.get(name=name)
            f = MonsterForm(request.POST, instance=m)
        else:
            f = MonsterForm(request.POST)

        if f.is_valid():
            f.save()
            return HttpResponseRedirect(reverse('browse_monsters'))
        else:
            return HttpResponse(str(f.errors))

    else:
        if name is not None:
            f = MonsterForm(instance=Monster.objects.get(name=name))
        else:
            f = MonsterForm()
    context = {'form': f,
               }
    return render(request, 'monsters/create.html', context)

def deets(request):
    name = request.GET.get('name')
    m = Monster.objects.get(name=name)
    variables = model_to_dict(m)

    variables['name'] = variables['name'].title()

    if variables.get('traits') is not None:
        variables['traits'] = '<p><b>Traits</b>' + variables['traits'].replace('<b>', '<p><b>')

    variables['actions'] = '<p><b>Actions</b>' + variables['actions'].replace('<b>', '<p><b>')

    if variables.get('legendary_actions') is not None:
        variables['legendary_actions'] = '<p><b>Legendary Actions</b><p>' + variables['legendary_actions'].replace('<b>', '<p><b>')
    else:
        del variables['legendary_actions']

    if variables.get('saving_throws') is not None:
        saving_throws = json.loads(variables['saving_throws'])
        variables['saving_throws'] = ', '.join([key + ' ' + signed_string(saving_throws[key]) for key in saving_throws]) + ' '

    for key in ['str_mod', 'dex_mod', 'con_mod', 'wis_mod', 'int_mod', 'cha_mod']:
        variables[key] = signed_string(variables[key], is_ability_score=True)

    for key in variables:
        try:
            variables[key] = rolls2links(variables[key])
        except:
            pass#print(traceback.format_exc())

    return render(request, 'monsters/details.html', variables)
