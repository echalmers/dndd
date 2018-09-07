from django.shortcuts import render
from django.http import HttpResponse
from util import df_to_text
import pandas as pd
from monsters.models import Monster


def browse(request):
    m = Monster.objects.all().values()
    df = pd.DataFrame.from_records(m)
    df = df[['name', 'type', 'hp', 'ac', 'speed', 'cr', 'xp']]
    df = df.sort_values('cr')

    variables = df_to_text(df, 'monster')

    return render(request, 'monsters/browse.html', variables)

def custom(request):
    return render(request, 'monsters/custom.html' )

def scrape(request):
    return render(request, 'monsters/scrape.html' )