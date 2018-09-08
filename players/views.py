from django.shortcuts import render

def browse(request):
    return render(request, 'players/browse.html')

def create(request):
    return render(request, 'players/create.html')
