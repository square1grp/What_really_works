from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from datetime import datetime


class RegisterPage(View):
    template_name = 'pages/register.html'

    def getEthnicityList(self):
        return {
            'European': [
                'Northwestern European',
                'Eastern European',
                'Southern European',
                'Ashkenazi Jewish'
                'Broadly European'
            ],
            'Central & South Asian': [
                'Central Asian, Northern Indian & Pakistani',
                'Southern Indian Subgroup',
                'Southern South Asian',
                'Broadly Central & South Asian'
            ],
            'East Asian & Native American': [
                'Chinese & Southeast Asian',
                'Japanese & Korean',
                'Northern Asian',
                'Native American',
                'Broadly East Asian & Native American'
            ],
            'Sub-Saharan African': [
                'West African',
                'Northern East African',
                'Congolese & Southern East African',
                'African Hunter-Gatherer',
                'Broadly Sub-Saharan African'
            ],
            'Western Asian & North African': [
                'Arab, Egyptian & Levantine',
                'North African',
                'Northern West Asian',
                'Broadly Western Asian & North African'
            ],
            'Melanesian': [
                'Broadly Melanesian'
            ]
        }

    def get(self, request, *args, **kwargs):
        years = [r for r in range(1900, datetime.today().year+1)]
        years.reverse()

        ethnicity_list = self.getEthnicityList()

        return render(request, self.template_name, dict(years=years, ethnicity_list=ethnicity_list))
