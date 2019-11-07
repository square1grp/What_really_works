from django.shortcuts import render, redirect
from .models import *


# Create your views here.


def index(request):
    user_id = int(1)

    return redirect('user/%s' % user_id)


def user_page(request, user_id):
    user = User.objects.get(id=user_id)
    user_symptoms = user.getSymptoms()

    return render(request, 'pages/user.html', dict(
        user=user,
        user_symptoms=user_symptoms
    ))


def symptom_page(request, symptom_id):
    symptom = Symptom.objects.get(id=symptom_id)
    users = UserSymptom.getUsersBySymptom(symptom_id)

    methods = []
    for user in users:
        methods = list(dict.fromkeys(
            methods + user.getMethods()))

    methods = [dict(
        id=method.id,
        name=method.name,
        effectiveness=method.getAvgEffectivenessScore(),
        drawbacks=method.getAvgDrawbacksScore(),
        user_count=method.getUsersByMethod(True)
    ) for method in methods]

    return render(request, 'pages/symptom.html', dict(
        symptom=symptom,
        methods=methods
    ))


def method_page(request, symptom_id, method_id):
    symptom = Symptom.objects.get(id=symptom_id)
    method = Method.objects.get(id=method_id)

    return render(request, 'pages/method.html', dict(
        symptom=symptom,
        method=method
    ))
