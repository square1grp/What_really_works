from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from wrw.models import User, Symptom, UserSymptom
from datetime import datetime
import pytz


class UserSymptomPage(View):
    template_name = 'pages/user-symptom.html'

    def addUserSymptom(self, params):
        user = User.objects.get(id=params['user_id'])
        symptom = Symptom.objects.get(id=params['symptom_id'])
        created_at = datetime.strptime(
            params['created_at'], '%m/%d/%Y').astimezone(pytz.timezone('UTC')).date()

        try:
            user_symptom = UserSymptom(
                user=user, symptom=symptom, created_at=created_at)
            user_symptom.save()
        except:
            pass

    def post(self, request, *args, **kwargs):
        params = request.POST

        if params['action'] == 'add':
            self.addUserSymptom(request.POST)
        elif params['action'] == 'delete':
            UserSymptom.objects.get(id=params['user_symptom_id']).delete()

        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user_id = kwargs['user_id'] if 'user_id' in kwargs else None

        if user_id is None:
            return HttpResponse('Provided Parameter is invalid.')

        try:
            user = User.objects.get(id=user_id)
        except:
            return HttpResponse('No user.')

        user = User.objects.get(id=user_id)
        user_symptoms = []
        for symptom in user.getSymptoms():
            user_symptoms += UserSymptom.objects.filter(
                user=user, symptom=symptom)

        symptoms = []
        for symptom in Symptom.objects.all():
            if symptom.id not in [user_symptom.symptom.id for user_symptom in user_symptoms]:
                symptoms.append(symptom)

        user_symptoms = [dict(
            id=user_symptom.id,
            symptom=user_symptom.getSymptomName(),
            created_at=user_symptom.getCreatedAt()
        ) for user_symptom in user_symptoms]

        user_symptoms.sort(key=lambda x: x['created_at'])

        return render(request, self.template_name, {
            'user_id': user_id,
            'user_symptoms': user_symptoms,
            'symptoms': symptoms
        })
