from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from util import df_to_text
import pandas as pd
from monsters.models import Monster
from .forms import NewMonsterForm
from django.urls import reverse


def browse(request):
    m = Monster.objects.all().values()
    df = pd.DataFrame.from_records(m)
    df = df[['name', 'type', 'hp', 'ac', 'speed', 'cr', 'xp']]
    df = df.sort_values('cr')

    variables = df_to_text(df, 'monster')

    return render(request, 'monsters/browse.html', variables)

def custom(request):
    return render(request, 'monsters/create.html' )

def scrape(request):
    return render(request, 'monsters/scrape.html' )

def create(request):

    if request.method == 'POST':
        # create form
        creation_form = NewMonsterForm(request.POST)

        if creation_form.is_valid():
            print(creation_form.name)

        return HttpResponseRedirect(reverse('browse'))

    else:
        creation_form = NewMonsterForm(instance=Monster.objects.filter(name='Weasel')[0])
        context = {'form': creation_form,
                   }
        return render(request, 'monsters/create.html', context)