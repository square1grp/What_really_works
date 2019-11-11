from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from .utils import *


# Create your views here.
def index(request):
    user_id = int(1)
    return redirect('user/%s' % user_id)
    return HttpResponse("Hello, world. You're at the polls index.")


def user_page(request, user_id):
    user = User.objects.get(id=user_id)
    user_symptoms = user.getSymptoms()

    return render(request, 'pages/user.html', dict(
        user=user,
        user_symptoms=user_symptoms
    ))


def symptom_page(request, symptom_id):
    symptom = Symptom.objects.get(id=symptom_id)
    users = getUsersBySymptom(symptom)

    methods = []
    for user in users:
        methods = list(dict.fromkeys(
            methods + user.getMethodsBySymptom(symptom)))

    methods = [dict(
        id=method.id,
        name=method.name,
        effectiveness=method.getAvgEffectivenessScore(symptom),
        drawbacks=method.getAvgDrawbackScore(symptom),
        user_count=len(method.getUsersHaveSymptom(symptom))
    ) for method in methods]

    return render(request, 'pages/symptom.html', dict(
        symptom=symptom,
        methods=methods
    ))


def method_page(request, symptom_id, method_id):
    symptom = Symptom.objects.get(id=symptom_id)
    method = Method.objects.get(id=method_id)

    (e_score_list, d_score_list) = method.getStatistics(symptom)

    e_statistics_data = getStatisticsData(e_score_list)
    d_statistics_data = getStatisticsData(d_score_list, True)

    statisticschart_content = getStatisticsChart(
        e_statistics_data, d_statistics_data)

    return render(request, 'pages/method.html', dict(
        symptom=symptom,
        method=method,
        statisticschart_content=statisticschart_content
    ))
