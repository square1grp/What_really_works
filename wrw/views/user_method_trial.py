from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from wrw.models import User, UserSymptom, Method, SymptomSeverity, SideEffectSeverity


class UserMethodTrialPage(View):
    template_name = 'pages/user-method-trial.html'

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

        user_symptoms = [dict(
            id=user_symptom.id,
            symptom=user_symptom.getSymptomName(),
            checked=False,
            created_at=user_symptom.getCreatedAt()
        ) for user_symptom in user_symptoms]
        methods = Method.objects.all()

        symptom_severities = SymptomSeverity.objects.all()
        side_effect_severities = SideEffectSeverity.objects.all()

        return render(request, self.template_name, {
            'user_id': user_id,
            'methods': methods,
            'user_symptoms': user_symptoms,
            'symptom_severities': symptom_severities,
            'side_effect_severities': side_effect_severities
        })
