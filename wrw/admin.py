from django.contrib import admin
from .models import *


class SymptomAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class UserSymptomAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'get_symptom']
    search_fields = ['user__name', 'symptom__name']

    def get_user(self, obj):
        return obj.getUserName()

    get_user.short_description = 'User'
    get_user.admin_order_field = 'user'

    def get_symptom(self, obj):
        return obj.getSymptomName()

    get_symptom.short_description = 'Symptom'
    get_symptom.admin_order_field = 'symptom'


class MethodAdmin(admin.ModelAdmin):
    search_fields = ['name']


class UserSeverityAdmin(admin.ModelAdmin):
    list_display = ['severity', 'title', 'date']


class UserMethodTrialAdmin(admin.ModelAdmin):
    list_display = ['get_method', 'get_user', 'get_symptom']
    search_fields = ['method__name',
                     'user_symptom__user__name', 'user_symptom__symptom__name']

    def get_method(self, obj):
        return obj.getMethodName()

    get_method.short_description = 'Treatment'
    get_method.admin_order_field = 'method'

    def get_user(self, obj):
        return obj.getUserName()

    get_user.short_description = 'User'
    get_user.admin_order_field = 'user_symptom__user'

    def get_symptom(self, obj):
        return obj.getSymptomName()

    get_symptom.short_description = 'Symptom'
    get_symptom.admin_order_field = 'user_symptom__symptom'


class UserMethodTrialStartSeverityAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'get_symptom', 'get_method', 'get_severity']
    search_fields = ['user_method_trial__user_symptom__user__name',
                     'user_method_trial__user_symptom__symptom__name', 'user_method_trial__method__name']

    def get_severity(self, obj):
        return obj.getSeverity()

    get_severity.short_description = 'Severity'

    def get_method(self, obj):
        return obj.getMethodName()

    get_method.short_description = 'Treatment'

    def get_user(self, obj):
        return obj.getUserName()

    get_user.short_description = 'User'

    def get_symptom(self, obj):
        return obj.getSymptomName()

    get_symptom.short_description = 'Symptom'


class UserMethodTrialEndSeverityAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'get_symptom', 'get_method',
                    'get_start_severity', 'get_end_severity']
    search_fields = ['user_method_trial__user_symptom__user__name',
                     'user_method_trial__user_symptom__symptom__name', 'user_method_trial__method__name']

    def get_end_severity(self, obj):
        return obj.getSeverity()

    get_end_severity.short_description = 'Severity (end)'

    def get_start_severity(self, obj):
        return obj.getStartSeverity()

    get_start_severity.short_description = 'Severity (start)'

    def get_method(self, obj):
        return obj.getMethodName()

    get_method.short_description = 'Treatment'

    def get_user(self, obj):
        return obj.getUserName()

    get_user.short_description = 'User'

    def get_symptom(self, obj):
        return obj.getSymptomName()

    get_symptom.short_description = 'Symptom'


admin.site.register(User)
admin.site.register(Symptom, SymptomAdmin)
admin.site.register(UserSymptom, UserSymptomAdmin)
admin.site.register(Method, MethodAdmin)
admin.site.register(UserSeverity, UserSeverityAdmin)
admin.site.register(UserMethodTrial, UserMethodTrialAdmin)
admin.site.register(UserMethodTrialStartSeverity,
                    UserMethodTrialStartSeverityAdmin)
admin.site.register(UserMethodTrialEndSeverity,
                    UserMethodTrialEndSeverityAdmin)
