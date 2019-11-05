from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from .models import User

# Create your views here.
def index(request):
    user_id = 1

    user = User.objects.get(id=user_id)
    user_symptoms = user.getSymptoms()

    return render(request, 'index.html', {
        'user': user,
        'user_symptoms': user_symptoms
    })