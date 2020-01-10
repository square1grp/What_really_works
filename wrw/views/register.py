from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from datetime import datetime
from wrw.models import User
from uuid import uuid4
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


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

    def post(self, request, *args, **kwargs):
        params = request.POST
        confirm_token = str(uuid4())

        user = User(
            username=params['username'],
            first_name=params['first_name'],
            last_name=params['last_name'],
            email=params['email'],
            birth_year=params['birth_year'],
            ethnicity_top=params['ethnicity_top'],
            ethnicity_second=params['ethnicity_second'],
            ethnicity_third=params['ethnicity_third'],
            gender=params['gender'],
            sexual_orientation=params['sexual_orientation'],
            password=params['password'],
            confirm_token=confirm_token,
            is_approved=False,
            address=params['address'],
            city=params['city'],
            state=params['state'],
            zipcode=params['zipcode'],
            country=params['country'],
        )

        href = 'http://127.0.0.1:8000/register/verify-token/%s' % confirm_token

        message = Mail(
            from_email='info@whatreallyworks.com',
            to_emails=params['email'],
            subject='Email verification',
            html_content='<a href="%s" target="_blank">Click here</a> or visit this URL on the browser: %s' % (href, href))

        sg = SendGridAPIClient(
            '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')
        sg.send(message)

        user.save()

        return HttpResponseRedirect('/register/verify-token/')

    def get(self, request, *args, **kwargs):
        years = [r for r in range(1900, datetime.today().year+1)]
        years.reverse()

        ethnicity_list = self.getEthnicityList()

        return render(request, self.template_name, dict(years=years, ethnicity_list=ethnicity_list))
