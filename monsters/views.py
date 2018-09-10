from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from util import df_to_text
import pandas as pd
from monsters.models import Monster
from .forms import MonsterForm
from django.urls import reverse


def browse(request):
    m = Monster.objects.all().values()
    df = pd.DataFrame.from_records(m)
    df = df[['name', 'type', 'hp', 'ac', 'speed', 'cr', 'xp']]
    df = df.sort_values(['cr', 'name'])

    df['actions'] = '<a href="create/' + df['name'] \
                    + '">clone/edit</a>   <a href="delete/' + df['name'] \
                    + '">delete</a>'
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
