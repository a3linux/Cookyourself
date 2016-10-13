from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(self):
    return HttpResponse("Here's the text of the Web page.", content_type="text/plain")
