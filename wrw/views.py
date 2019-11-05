from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, redirect
from .models import *

# Create your views here.
def index(request):
    user_id = int(1)

    return redirect('user/%s' % user_id)

def user(request, user_id):
    user = User.objects.get(id=user_id)
    user_symptoms = user.getSymptoms()

    return render(request, 'pages/user.html', {
        'user': user,
        'user_symptoms': user_symptoms
    })

def symptom(request, symptom_id):
    symptom = Symptom.objects.get(id=symptom_id)

    return render(request, 'pages/symptom.html', {
        'symptom': symptom
    })