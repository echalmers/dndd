from django.shortcuts import render
from .models import Player
import pandas as pd
from util import df_to_text
from .forms import PlayerForm
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse


def browse(request):

    players = Player.objects.all().values()
    df = pd.DataFrame.from_records(players)
    if len(df.index) > 0:
        df = df[['name', 'level', 'ac', 'initiative']]
    else:
        df = pd.DataFrame(columns=['name', 'level', 'ac', 'initiative'])

    df['actions'] = '<a href="create/' + df['name'] \
                    + '">clone/edit</a>   <a href="delete/' + df['name'] \
                    + '">delete</a>'

    pd.set_option('display.max_colwidth', -1)
    variables = {'table': df.fillna('').to_html(classes='datatable', escape=False, index=False)}

    return render(request, 'players/browse.html', variables)


def create(request, name=None):

    print(request)
    print(name)

    if request.method == 'POST':
        # if name is not None:
        #     p = Player.objects.get(name=name)
        #     f = PlayerForm(request.POST, instance=p)
        # else:
        try:
            p = Player.objects.get(name=request.POST.get('name'))
            f = PlayerForm(request.POST, instance=p)
        except Player.DoesNotExist:
            f = PlayerForm(request.POST)

        if f.is_valid():
            f.save()
            return HttpResponseRedirect(reverse('browse_players'))
        else:
            return HttpResponse(str(f.errors))

    elif request.method == 'GET':
        if name is not None:
            f = PlayerForm(instance=Player.objects.get(name=name))
        else:
            f = PlayerForm()
    context = {'form': f,
               }
    return render(request, 'players/create.html', context)


def delete(request, name):
    print(name)
    p = Player.objects.get(name=name)
    print(p.name)
    p.delete()
    return HttpResponseRedirect(reverse('browse_players'))
