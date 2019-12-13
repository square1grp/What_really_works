from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from wrw.models import User, SymptomSeverity, UserSymptom, UserSymptomUpdate
from datetime import datetime
import pytz


class UserSymptomUpdatePage(View):
    template_name = 'pages/user-symptom-update.html'

    def post(self, request, *args, **kwargs):
        user_id = kwargs['user_id'] if 'user_id' in kwargs else None

        if user_id is None:
            return HttpResponse('Provided Parameter is invalid.')

        try:
            params = request.POST

            if params['action'] == 'add':
                user_symptom = UserSymptom.objects.get(
                    id=params['user_symptom_id'])
                created_at = datetime.strptime('%s %s:%s:%s' % (
                    params['created_at'], params['created_at_h'], params['created_at_m'], params['created_at_s']), '%m/%d/%Y %H:%M:%S')
                symptom_severity = SymptomSeverity.objects.get(
                    id=params['symptom_severity_id'])

                user_symptom_update = UserSymptomUpdate(user_symptom=user_symptom, symptom_severity=symptom_severity,
                                                        created_at=created_at, title=params['title'], description=params['description'])

                user_symptom_update.save()
            else:
                UserSymptomUpdate.objects.get(id=params['id']).delete()
        except:
            pass

        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user_id = kwargs['user_id'] if 'user_id' in kwargs else None

        if user_id is None:
            return HttpResponse('Provided Parameter is invalid.')

        user = User.objects.get(id=user_id)

        user_symptoms = UserSymptom.objects.filter(
            user=user, symptom__in=user.getSymptoms())
        user_symptom_updates = UserSymptomUpdate.objects.filter(
            user_symptom__in=user_symptoms).order_by('-created_at', '-id')
        user_symptom_updates = [dict(
            id=user_symptom_update.id,
            title=user_symptom_update.getTitle(),
            symptom_severity=user_symptom_update.getSeverityAsText(),
            created_at=user_symptom_update.getCreatedAt().strftime('%Y-%m-%d %H:%M:%S')
        ) for user_symptom_update in user_symptom_updates]
        symptom_severities = SymptomSeverity.objects.all()

        return render(request, self.template_name, dict(
            user_id=user_id,
            user_symptom_updates=user_symptom_updates,
            user_symptoms=user_symptoms,
            symptom_severities=symptom_severities,
            hours=[dict(value=hour, title="{0:0=2d}".format(
                hour)) for hour in range(24)],
            minutes=[dict(value=minute, title="{0:0=2d}".format(
                minute)) for minute in range(60)],
            seconds=[dict(value=second, title="{0:0=2d}".format(
                second)) for second in range(60)],
            current_time=dict(h=datetime.now().hour,
                              m=datetime.now().minute,
                              s=datetime.now().second)
        ))
