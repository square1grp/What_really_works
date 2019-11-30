from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from wrw.models import Symptom, UserSymptom


class SymptomPage(View):
    template_name = 'pages/symptom.html'

    def getUsersBySymptom(self, symptom):
        users = [user_symptom.user
                 for user_symptom in UserSymptom.objects.filter(symptom=symptom)]

        return list(dict.fromkeys(users))

    def getMethodsUsedForSymptom(self, symptom):
        users = self.getUsersBySymptom(symptom)

        methods = []
        for user in users:
            methods += user.getMethodsBySymptom(symptom)

        return list(dict.fromkeys(methods))

    def get(self, request, *args, **kwargs):
        symptom_id = kwargs['symptom_id'] if 'symptom_id' in kwargs else None

        if symptom_id is None:
            return HttpResponse('Provided Parameter is invalid.')

        symptom = Symptom.objects.get(id=symptom_id)

        methods = self.getMethodsUsedForSymptom(symptom)

        rows = [dict(
            method=method,
            symptom_score=method.getAvgSymptomScore(symptom),
            side_effect_score=method.getAvgSideEffectScore(symptom),
            user_count=len(method.getUsersHaveSymptom(symptom))
        ) for method in methods]

        return render(request, 'pages/symptom.html', dict(
            symptom=symptom,
            rows=rows
        ))
