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
    users = UserSymptom.getUsersBySymptom(symptom_id)

    method_trials = []
    for user in users:
        method_trials = list(dict.fromkeys(
            method_trials + user.getMethodTrials()))

    method_trials = [{
        'id': method_trial.id,
        'name': method_trial.name,
        'effectiveness': 1,
        'drawbacks': 1,
        'user_count': 5
    } for method_trial in method_trials]

    return render(request, 'pages/symptom.html', {
        'symptom': symptom,
        'method_trials': method_trials
    })
