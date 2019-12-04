from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from wrw.models import User, SideEffectSeverity, UserSideEffectUpdate
from datetime import datetime
import pytz


class UserSideEffectUpdatePage(View):
    template_name = 'pages/user-side-effect-update.html'

    def post(self, request, *args, **kwargs):
        user_id = kwargs['user_id'] if 'user_id' in kwargs else None

        if user_id is None:
            return HttpResponse('Provided Parameter is invalid.')

        try:
            user = User.objects.get(id=user_id)

            params = request.POST

            if params['action'] == 'add':
                side_effect_severity = SideEffectSeverity.objects.get(
                    id=params['side_effect_severity_id'])
                created_at = datetime.strptime(
                    params['created_at'], '%m/%d/%Y').astimezone(pytz.timezone('UTC')).date()

                user_side_effect_update = UserSideEffectUpdate(user=user, side_effect_severity=side_effect_severity,
                                                               created_at=created_at, title=params['title'], description=params['description'])

                user_side_effect_update.save()
            else:
                UserSideEffectUpdate.objects.get(id=params['id']).delete()
        except:
            pass

        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user_id = kwargs['user_id'] if 'user_id' in kwargs else None

        if user_id is None:
            return HttpResponse('Provided Parameter is invalid.')

        user = User.objects.get(id=user_id)

        user_side_effect_updates = UserSideEffectUpdate.objects.filter(
            user=user).order_by('-created_at', '-id')
        user_side_effect_updates = [dict(
            id=user_side_effect_update.id,
            title=user_side_effect_update.getTitle(),
            side_effect_severity=user_side_effect_update.getSeverityAsText(),
            created_at=user_side_effect_update.getCreatedAt()
        ) for user_side_effect_update in user_side_effect_updates]
        side_effect_severities = SideEffectSeverity.objects.all()

        return render(request, self.template_name, dict(
            user_id=user_id,
            user_side_effect_updates=user_side_effect_updates,
            side_effect_severities=side_effect_severities
        ))
