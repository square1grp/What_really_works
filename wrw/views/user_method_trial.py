from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from wrw.models import User, UserSymptom, Method, SymptomSeverity, SideEffectSeverity, UserSideEffectUpdate, UserSymptomUpdate, UserMethodTrialStart, UserMethodTrialEnd
from datetime import datetime
import pytz
from datetime import timedelta


class UserMethodTrialPage(View):
    template_name = 'pages/user-method-trial.html'

    def addUserMethodTrialStart(self, user, method, created_at):
        user_method_trial_start = UserMethodTrialStart(
            user=user,
            method=method,
            created_at=created_at
        )
        user_method_trial_start.save()

        return user_method_trial_start

    def addUserMethodTrialEnd(self, user_method_trial_start, created_at):
        user_method_trial_end = UserMethodTrialEnd(
            user_method_trial_start=user_method_trial_start,
            created_at=created_at
        )
        user_method_trial_end.save()

        return user_method_trial_end

    def addUserSymptomUpdate(self, user_symptom, symptom_severity, user_method_trial_start, created_at, title, description):
        user_symptom_update = UserSymptomUpdate(
            user_symptom=user_symptom,
            symptom_severity=symptom_severity,
            user_method_trial_start=user_method_trial_start,
            created_at=created_at,
            title=title,
            description=description)
        user_symptom_update.save()

        return user_symptom_update

    def addUserSideEffectUpdate(self, user, side_effect_severity, user_method_trial_start, created_at, title, description):
        user_side_effect_update = UserSideEffectUpdate(
            user=user,
            side_effect_severity=side_effect_severity,
            user_method_trial_start=user_method_trial_start,
            created_at=created_at,
            title=title,
            description=description)
        user_side_effect_update.save()

        return user_side_effect_update

    def deleteUserTreatment(self, user, id):
        user_method_trial_start = UserMethodTrialStart.objects.get(
            id=id)

        if user_method_trial_start.isEnded():
            user_method_trial_end = user_method_trial_start.getEnded()
            '''
            ended_at = user_method_trial_start.getEndedAt()

            user_symptom_updates = UserSymptomUpdate.objects.filter(
                user_symptom__user=user, created_at=ended_at)
            for user_symptom_update in user_symptom_updates:
                user_symptom_update.delete()

            user_side_effect_updates = UserSideEffectUpdate.objects.filter(
                user=user, created_at=ended_at)
            for user_side_effect_update in user_side_effect_updates:
                user_side_effect_update.delete()
            '''

            user_method_trial_end.delete()
        '''
        started_at = user_method_trial_start.getStartedAt()

        user_symptom_updates = UserSymptomUpdate.objects.filter(
            user_symptom__user=user, created_at=started_at)
        for user_symptom_update in user_symptom_updates:
            user_symptom_update.delete()

        user_side_effect_updates = UserSideEffectUpdate.objects.filter(
            user=user, created_at=started_at)
        for user_side_effect_update in user_side_effect_updates:
            user_side_effect_update.delete()
        '''

        user_method_trial_start.delete()

    def post(self, request, *args, **kwargs):
        user_id = kwargs['user_id'] if 'user_id' in kwargs else None

        if user_id is None:
            return HttpResponse('Provided Parameter is invalid.')

        try:
            user = User.objects.get(id=user_id)

            params = request.POST

            if params['action'] == 'add':
                method = Method.objects.get(id=params['method_id'])
                started_at = datetime.strptime(
                    params['started_at'], '%m/%d/%Y').astimezone(pytz.timezone('UTC'))
                start_side_effect_severity = SideEffectSeverity.objects.get(
                    id=params['start_side_effect_severity_id'])

                user_method_trial_start = self.addUserMethodTrialStart(
                    user, method, started_at)

                self.addUserSideEffectUpdate(
                    user, start_side_effect_severity, user_method_trial_start, started_at, params['start_title'], params['start_description'])

                if 'is_ended' in params and params['is_ended'] == 'yes':
                    end_side_effect_severity = SideEffectSeverity.objects.get(
                        id=params['end_side_effect_severity_id'])
                    ended_at = datetime.strptime(
                        params['ended_at'], '%m/%d/%Y').astimezone(pytz.timezone('UTC'))

                    if started_at == ended_at:
                        ended_at = ended_at + timedelta(days=1)

                    self.addUserMethodTrialEnd(
                        user_method_trial_start, ended_at)

                    self.addUserSideEffectUpdate(
                        user, end_side_effect_severity, user_method_trial_start, ended_at, params['end_title'], params['end_description'])

                for symptom in user.getSymptoms():
                    user_symptom = UserSymptom.objects.get(
                        user=user, symptom=symptom)

                    start_symptom_severity_id = params['start_symptom_severity_id_%s' %
                                                       user_symptom.id]
                    start_symptom_severity = SymptomSeverity.objects.get(
                        id=start_symptom_severity_id)

                    self.addUserSymptomUpdate(
                        user_symptom, start_symptom_severity, user_method_trial_start, started_at, params['start_title'], params['start_description'])

                    if 'is_ended' in params and params['is_ended'] == 'yes':
                        end_symptom_severity_id = params['end_symptom_severity_id_%s' %
                                                         user_symptom.id]
                        end_symptom_severity = SymptomSeverity.objects.get(
                            id=end_symptom_severity_id)

                        self.addUserSymptomUpdate(
                            user_symptom, end_symptom_severity, user_method_trial_start, ended_at, params['end_title'], params['end_description'])

            elif params['action'] == 'delete':
                self.deleteUserTreatment(user, params['id'])

        except:
            return HttpResponse('Internal Server Error.')

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
        user_symptoms = UserSymptom.objects.filter(
            user=user, symptom__in=user.getSymptoms())

        user_symptoms = [dict(
            id=user_symptom.id,
            symptom=user_symptom.getSymptomName(),
            checked=False,
            created_at=user_symptom.getCreatedAt()
        ) for user_symptom in user_symptoms]

        methods = Method.objects.all()
        user_treatments = []
        for method in methods:
            user_method_trial_starts = UserMethodTrialStart.objects.filter(
                user=user, method=method)

            for user_method_trial_start in user_method_trial_starts:
                ended_at = user_method_trial_start.getEndedAt()

                user_treatments.append(dict(
                    id=user_method_trial_start.id,
                    method_name=user_method_trial_start.getMethodName(),
                    started_at=user_method_trial_start.getStartedAt().strftime('%Y-%m-%d %H:%M:%S'),
                    ended_at=ended_at.strftime('%Y-%m-%d %H:%M:%S') if ended_at is not None else None
                ))

        user_treatments.sort(key=lambda x: x['started_at'])
        user_treatments.reverse()

        symptom_severities = SymptomSeverity.objects.all()
        side_effect_severities = SideEffectSeverity.objects.all()

        return render(request, self.template_name, dict(
            user_id=user_id,
            user_treatments=user_treatments,
            methods=methods,
            user_symptoms=user_symptoms,
            symptom_severities=symptom_severities,
            side_effect_severities=side_effect_severities
        ))
