from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Symptom)
admin.site.register(Method)
admin.site.register(UserSymptom)
admin.site.register(UserMethodTrial)
admin.site.register(UserSeverityUpdate)
admin.site.register(UserMethodTrialStartUpdate)
admin.site.register(UserMethodTrialEndUpdate)