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

    def updateUserMethodTrialStart(self, umts_id, method, started_at):
        user_method_trial_start = UserMethodTrialStart.objects.get(id=umts_id)
        user_method_trial_start.method = method
        user_method_trial_start.created_at = started_at

        user_method_trial_start.save()

        return user_method_trial_start

    def addUserMethodTrialEnd(self, user_method_trial_start, created_at):
        user_method_trial_end = UserMethodTrialEnd(
            user_method_trial_start=user_method_trial_start,
            created_at=created_at
        )
        user_method_trial_end.save()

        return user_method_trial_end

    def updateUserMethodTrialEnd(self, user_method_trial_start, created_at):
        if not user_method_trial_start.isEnded():
            return self.addUserMethodTrialEnd(user_method_trial_start, created_at)

        user_method_trial_end = UserMethodTrialEnd.objects.get(
            user_method_trial_start=user_method_trial_start)

        user_method_trial_end.created_at = created_at
        user_method_trial_end.save()

        return user_method_trial_end

    def deleteUserMethodTrialEnd(self, user_method_trial_start):
        if not user_method_trial_start.isEnded():
            return

        user_method_trial_end = UserMethodTrialEnd.objects.get(
            user_method_trial_start=user_method_trial_start)

        user_method_trial_end.delete()

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

    def deleteUserSymptomUpdates(self, user_method_trial_start):
        user_symptom_updates = UserSymptomUpdate.objects.filter(
            user_method_trial_start=user_method_trial_start)

        for user_symptom_update in user_symptom_updates:
            user_symptom_update.delete()

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

    def deleteUserSideEffectUpdates(self, user_method_trial_start):
        user_side_effect_updates = UserSideEffectUpdate.objects.filter(
            user_method_trial_start=user_method_trial_start)

        for user_side_effect_update in user_side_effect_updates:
            user_side_effect_update.delete()

    def deleteUserTreatment(self, user, id):
        user_method_trial_start = UserMethodTrialStart.objects.get(
            id=id)

        if user_method_trial_start.isEnded():
            user_method_trial_end = user_method_trial_start.getEnded()

            user_method_trial_end.delete()

        user_symptom_updates = UserSymptomUpdate.objects.filter(
            user_method_trial_start=user_method_trial_start)
        for user_symptom_update in user_symptom_updates:
            user_symptom_update.delete()

        user_side_effect_updates = UserSideEffectUpdate.objects.filter(
            user_method_trial_start=user_method_trial_start)
        for user_side_effect_update in user_side_effect_updates:
            user_side_effect_update.delete()

        user_method_trial_start.delete()

    def post(self, request, *args, **kwargs):
        user_id = kwargs['user_id'] if 'user_id' in kwargs else None

        if user_id is None:
            return HttpResponse('Provided Parameter is invalid.')

        user = User.objects.get(id=user_id)

        params = request.POST

        try:
            if params['action'] == 'add':
                umts_id = params['umts_id'] if 'umts_id' in params else None

                method = Method.objects.get(id=params['method_id'])
                started_at = datetime.strptime(
                    params['started_at'], '%m/%d/%Y').astimezone(pytz.timezone('UTC'))
                start_side_effect_severity = SideEffectSeverity.objects.get(
                    id=params['start_side_effect_severity_id'])

                if umts_id is not None:
                    user_method_trial_start = self.updateUserMethodTrialStart(
                        umts_id, method, started_at)

                    self.deleteUserSideEffectUpdates(user_method_trial_start)
                    self.deleteUserSymptomUpdates(user_method_trial_start)
                else:
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

                    if umts_id is not None:
                        self.updateUserMethodTrialEnd(
                            user_method_trial_start, ended_at)
                    else:
                        self.addUserMethodTrialEnd(
                            user_method_trial_start, ended_at)

                    self.addUserSideEffectUpdate(
                        user, end_side_effect_severity, user_method_trial_start, ended_at, params['end_title'], params['end_description'])
                elif umts_id is not None:
                    self.deleteUserMethodTrialEnd(user_method_trial_start)

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
            elif params['action'] == 'edit':
                kwargs['umts_id'] = params['id']
        except:
            pass

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
                    ended_at=ended_at.strftime(
                        '%Y-%m-%d %H:%M:%S') if ended_at is not None else None
                ))

        edit_umts = None
        umts_id = kwargs['umts_id'] if 'umts_id' in kwargs else None

        if umts_id is not None:
            edit_umts = UserMethodTrialStart.objects.get(id=umts_id)

            is_ended = edit_umts.isEnded()
            ended_at = edit_umts.getEndedAt()
            ended_symptom_severity = edit_umts.getEndedSymptomSeverity()
            ended_side_effect_update = edit_umts.getEndedSideEffectUpdate()

            edit_umts = dict(
                method=edit_umts.getMethod(),
                started_at=edit_umts.getStartedAt().strftime('%m/%d/%Y'),
                is_ended=is_ended,
                ended_at=ended_at.strftime(
                    '%m/%d/%Y') if ended_at is not None else ended_at,
                started_symptom_severity=edit_umts.getStartedSymptomSeverity(),
                ended_symptom_severity=ended_symptom_severity,
                started_side_effect_severity=edit_umts.getStartedSideEffectSeverity(),
                started_title=edit_umts.getStartedSideEffectUpdate().getTitle(),
                started_description=edit_umts.getStartedSideEffectUpdate().getDescription(),
                ended_side_effect_severity=edit_umts.getEndedSideEffectSeverity(),
                ended_title=ended_side_effect_update.getTitle(
                ) if ended_side_effect_update is not None else '',
                ended_description=ended_side_effect_update.getDescription() if ended_side_effect_update is not None else '')

        user_treatments.sort(key=lambda x: x['started_at'])
        user_treatments.reverse()

        symptom_severities = SymptomSeverity.objects.all()
        side_effect_severities = SideEffectSeverity.objects.all()

        return render(request, self.template_name, dict(
            user_id=user_id,
            user_treatments=user_treatments,
            methods=methods,
            user_symptoms=user_symptoms,
            umts_id=umts_id,
            edit_umts=edit_umts,
            symptom_severities=symptom_severities,
            side_effect_severities=side_effect_severities
        ))
