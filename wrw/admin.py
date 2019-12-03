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


class UserMethodTrialStartAdmin(admin.ModelAdmin):
    list_display = ['user', 'getMethodName', 'created_at']
    search_fields = ['user__name', 'method__name']


class UserMethodTrialEndAdmin(admin.ModelAdmin):
    list_display = ['getUserName', 'getMethodName',
                    'getStartedAt', 'created_at']
    search_fields = ['method_trial_start__user__name', 'method__name']


class UserSymptomUpdateAdmin(admin.ModelAdmin):
    list_display = ['getUserName', 'getSymptomName',
                    'title', 'getSeverityAsText', 'created_at']


admin.site.register(User, UserAdmin)
admin.site.register(Symptom, SymptomAdmin)
admin.site.register(UserSymptom, UserSymptomAdmin)
admin.site.register(Method, MethodAdmin)
admin.site.register(SymptomSeverity, SymptomSeverityAdmin)
admin.site.register(SideEffectSeverity, SideEffectSeverityAdmin)
admin.site.register(UserSideEffectUpdate, UserSideEffectUpdateAdmin)
admin.site.register(UserMethodTrialStart, UserMethodTrialStartAdmin)
admin.site.register(UserMethodTrialEnd, UserMethodTrialEndAdmin)
admin.site.register(UserSymptomUpdate, UserSymptomUpdateAdmin)
