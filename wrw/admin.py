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


class UserMethodTrialStartAdmin(admin.ModelAdmin):
    list_display = ['getMethodName', 'getDrawback', 'created_at']
    search_fields = ['method__name']
    list_filter = ['drawback__rating']


class UserMethodTrialEndAdmin(admin.ModelAdmin):
    list_display = ['getMethodName', 'getDrawback', 'created_at']
    search_fields = ['method__name']
    list_filter = ['drawback__rating']


class UserSymptomTrialStartAdmin(admin.ModelAdmin):
    list_display = ['getMethodName', 'getSeverity', 'getDrawback']
    search_fields = ['user_method_trial_start__method__name']
    list_filter = ['severity__rating',
                   'user_method_trial_start__drawback__rating']


class UserSymptomTrialEndAdmin(admin.ModelAdmin):
    list_display = ['getMethodName', 'getSeverity', 'getDrawback']
    search_fields = [
        'user_symptom_trial_start__user_method_trial_start__method__name']
    list_filter = ['user_symptom_trial_start__severity__rating',
                   'user_symptom_trial_start__user_method_trial_start__drawback__rating',
                   'severity__rating', 'user_method_trial_end__drawback__rating']


class UserSymptomAdmin(admin.ModelAdmin):
    list_display = ['getUserName', 'getSymptomName', 'getStartSeverity',
                    'getStartDrawback', 'getEndSeverity', 'getEndDrawback']
    search_fields = ['user__name', 'symptom__name',
                     'user_symptom_trial_start__user_method_trial_start__method__name']
    list_filter = [
        'user_symptom_trial_start__severity__rating', 'user_symptom_trial_start__user_method_trial_start__drawback__rating',
        'user_symptom_trial_end__severity__rating', 'user_symptom_trial_end__user_method_trial_end__drawback__rating']


class UserSymptomUpdateAdmin(admin.ModelAdmin):
    list_display = ['getUserName', 'getSymptomName',
                    'getSeverity', 'getSeverity', 'getDrawback', 'created_at']
    search_fields = ['user_symptom__user__name', 'user_symptom__symptom__name']
    list_filter = ['severity__rating', 'drawback__rating']


admin.site.register(User, UserAdmin)
admin.site.register(Symptom, SymptomAdmin)
admin.site.register(Method, MethodAdmin)
admin.site.register(Severity, SeverityAdmin)
admin.site.register(Drawback, DrawbackAdmin)
admin.site.register(UserSymptom, UserSymptomAdmin)
admin.site.register(UserSymptomUpdate, UserSymptomUpdateAdmin)
admin.site.register(UserMethodTrialStart, UserMethodTrialStartAdmin)
admin.site.register(UserMethodTrialEnd, UserMethodTrialEndAdmin)
admin.site.register(UserSymptomTrialStart, UserSymptomTrialStartAdmin)
admin.site.register(UserSymptomTrialEnd, UserSymptomTrialEndAdmin)
