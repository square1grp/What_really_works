from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views import View
from wrw.models import User


class VerifyTokenPage(View):
    template_name = 'pages/verify.html'

    def get(self, request, *args, **kwargs):
        if 'token' in kwargs:
            confirm_token = kwargs['token']

            if confirm_token[-1] == '/':
                confirm_token = confirm_token[:-1]

            try:
                import pdb; pdb.set_trace()
                user = User.objects.get(confirm_token=confirm_token)

                user.is_approved = True
                user.save()
            except ObjectDoesNotExist:
                return HttpResponse("return this string")

        return render(request, self.template_name)
