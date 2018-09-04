from django.shortcuts import render
from django.http import HttpResponse

def browse(request):
    return render(request, 'monsters/browse.html' )

def custom(request):
    return render(request, 'monsters/custom.html' )

def scrape(request):
    return render(request, 'monsters/scrape.html' )