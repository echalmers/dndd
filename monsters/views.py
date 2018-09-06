from django.shortcuts import render
from django.http import HttpResponse
from util import df_to_text
import pandas as pd
from monsters.models import Monster


def browse(request):
    m = Monster.objects.all()
    df = pd.DataFrame.from_records(m)
    variables = df_to_text(df, 'monthly_breakdown')

    return render(request, 'monsters/browse.html' )

def custom(request):
    return render(request, 'monsters/custom.html' )

def scrape(request):
    return render(request, 'monsters/scrape.html' )