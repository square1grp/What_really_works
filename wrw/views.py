from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from .utils import *


# Create your views here.
# index page
def index(request):
    user_id = int(1)
    return redirect('user/%s' % user_id)
    return HttpResponse('Hello, world. You\'re at the polls index.')


# single user page
def user_page(request, user_id):
    user = User.objects.get(id=user_id)
    symptoms = user.getSymptoms()
    treatment_timeline = getTreatmentGanttChart(
        user.getAllSymptomTrialsStarted())

    symptom_timelines = getSymptomTimelines(user, symptoms)

    return render(request, 'pages/user.html', dict(
        user=user,
        symptoms=symptoms,
        treatment_timeline=treatment_timeline,
        symptom_timelines=symptom_timelines
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
        effectiveness=method.getAverageScore(symptom, True),
        drawbacks=method.getAverageScore(symptom, False),
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

    user_timelines = []
    users = method.getUsersHaveSymptom(symptom)
    for user in users:
        symptom_timeline = getSymptomTimelines(user, [symptom], 200)[0]
        user_timelines.append(
            dict(user=user, symptom_timeline=symptom_timeline))

    return render(request, 'pages/method.html', dict(
        symptom=symptom,
        method=method,
        statisticschart_content=statisticschart_content,
        user_timelines=user_timelines
    ))


def add_symptom_page(request, user_id):
    if request.method == 'POST':
        try:
            params = request.POST

            if params['action'] == 'add':
                addUserSymptom(request.POST)
            elif params['action'] == 'delete':
                UserSymptom.objects.get(id=params['user_symptom_id']).delete()

        except:
            pass

    user = User.objects.get(id=user_id)
    user_symptoms = []
    for symptom in user.getSymptoms():
        user_symptoms += UserSymptom.objects.filter(user=user, symptom=symptom)

    user_symptoms = [dict(
        id=user_symptom.id,
        symptom=user_symptom.getSymptomName(),
        created_at=user_symptom.getCreatedAt()
    ) for user_symptom in user_symptoms]
    user_symptoms.sort(key=lambda x: x['created_at'])

    symptoms = getAllSymptoms()

    return render(request, 'pages/add/user_symptom.html', {
        'user_id': user_id,
        'user_symptoms': user_symptoms,
        'symptoms': symptoms
    })
