from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View


class IndexPage(View):
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect('/user/1')
        # return render(request, self.template_name)
