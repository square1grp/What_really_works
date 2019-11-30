from django.contrib import admin
from .models import *


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title

            return instance

    return Wrapper

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


class SymptomSeverityAdmin(admin.ModelAdmin):
    list_display = ['getSeverityAsText', 'title']
    search_fields = ['title']
    list_filter = ['rating']


class SideEffectSeverityAdmin(admin.ModelAdmin):
    list_display = ['getSeverityAsText', 'title']
    search_fields = ['title']
    list_filter = ['rating']


class UserSideEffectUpdateAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'getSeverityAsText', 'created_at']
    search_fields = ['user__name', 'title']
    list_filter = [('side_effect_severity__rating',
                    custom_titled_filter('Side Effect Severity'))]


class UserSymptomAdmin(admin.ModelAdmin):
    list_display = ['user', 'symptom']
    search_fields = ['user__name', 'symptom__name']


class MethodTrialStartAdmin(admin.ModelAdmin):
    list_display = ['getMethodName', 'created_at']
    search_fields = ['method__name']


class MethodTrialEndAdmin(admin.ModelAdmin):
    list_display = ['getMethodName', 'created_at']
    search_fields = ['method__name']


class SymptomTrialStartAdmin(admin.ModelAdmin):
    list_display = ['getMethodName', 'created_at']
    search_fields = ['method_trial_start__method__name']


class SymptomTrialEndAdmin(admin.ModelAdmin):
    list_display = ['getMethodName', 'created_at']
    search_fields = ['symptom_trial_start__method_trial_start__method__name']


class UserSymptomUpdateAdmin(admin.ModelAdmin):
    list_display = ['getUserName', 'getSymptomName', 'title', 'getSeverityAsText',
                    'getMethodName', 'getStartedAt', 'getEndedAt', 'created_at']


admin.site.register(User, UserAdmin)
admin.site.register(Symptom, SymptomAdmin)
admin.site.register(UserSymptom, UserSymptomAdmin)
admin.site.register(Method, MethodAdmin)
admin.site.register(SymptomSeverity, SymptomSeverityAdmin)
admin.site.register(SideEffectSeverity, SideEffectSeverityAdmin)
admin.site.register(UserSideEffectUpdate, UserSideEffectUpdateAdmin)
admin.site.register(MethodTrialStart, MethodTrialStartAdmin)
admin.site.register(MethodTrialEnd, MethodTrialEndAdmin)
admin.site.register(SymptomTrialStart, SymptomTrialStartAdmin)
admin.site.register(SymptomTrialEnd, SymptomTrialEndAdmin)
admin.site.register(UserSymptomUpdate, UserSymptomUpdateAdmin)
