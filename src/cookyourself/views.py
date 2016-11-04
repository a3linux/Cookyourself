from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'main.html')

def dish(request, id=0):
    return render(request, 'dish.html')

def shoppinglist(request):
    return render(request, 'shoppinglist.html')

def recommendation(request):
    return render(request, 'recommendation.html')

def profile(request, id=0):
    return render(request, 'profile_i_made_it.html')
