from django.contrib import admin
from .models import *


# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class SymptomAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class MethodAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class SeverityAdmin(admin.ModelAdmin):
    list_display = ['getRatingText', 'title']
    search_fields = ['title']
    list_filter = ['rating']


class DrawbackAdmin(admin.ModelAdmin):
    list_display = ['getRatingText', 'title']
    search_fields = ['title']
    list_filter = ['rating']


class UserSymptomAdmin(admin.ModelAdmin):
    list_display = ['getUserName', 'getSymptomName']
    search_fields = ['user__name', 'symptom__name']


class UserSymptomUpdateAdmin(admin.ModelAdmin):
    list_display = ['getUserName', 'getSymptomName',
                    'getSeverity', 'updated_at']
    search_fields = ['user_symptom__user__name', 'user_symptom__symptom__name']
    list_filter = ['severity__rating']


class UserMethodTrialStartAdmin(admin.ModelAdmin):
    list_display = ['getUserName', 'getSymptomName', 'getMethodName',
                    'getSeverity', 'started_at']
    search_fields = ['user_symptom__user__name',
                     'user_symptom__symptom__name', 'method__name']
    list_filter = ['severity__rating',
                   'user_symptom__symptom__name', 'method__name']


admin.site.register(User, UserAdmin)
admin.site.register(Symptom, SymptomAdmin)
admin.site.register(Method, MethodAdmin)
admin.site.register(Severity, SeverityAdmin)
admin.site.register(Drawback, DrawbackAdmin)
admin.site.register(UserSymptom, UserSymptomAdmin)
admin.site.register(UserSymptomUpdate, UserSymptomUpdateAdmin)
admin.site.register(UserMethodTrialStart, UserMethodTrialStartAdmin)
admin.site.register(UserMethodTrialEnd)
