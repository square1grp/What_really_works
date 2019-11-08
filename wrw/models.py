from django.db import models
from datetime import datetime
from statistics import *


SEVERITIES = [
    (0, 'None'),
    (1, 'Mild'),
    (2, 'Moderate'),
    (3, 'Severe'),
    (4, 'Very Severe')
]


# User Model
class User(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    @staticmethod
    def getUsersBySymptom(symptom_id):
        users = []

        for symptom in UserSymptom.objects.filter(symptom__id=symptom_id):
            users.append(symptom.user)

        return users

    def getSymptoms(self):
        return [user_symptom.symptom for user_symptom in UserSymptom.objects.filter(user=self)]

    def getSymptom(self, symptom_id):
        symptoms = UserSymptom.objects.filter(
            user=self, symptom__id=symptom_id)

        return symptoms[0] if len(symptoms) else None

    # get methods
    def getMethodsBySymptom(self, symptom_id, no_duplicate=True):
        symptom = self.getSymptom(symptom_id)

        methods = []
        if symptom:
            method_trials = UserMethodTrial.objects.filter(
                user_symptom=symptom)

            methods = [method_trial.method for method_trial in method_trials]

            if no_duplicate:
                return list(dict.fromkeys(methods))

        return methods


# Symptom Model
class Symptom(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


# User Symptom Model
class UserSymptom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'symptom']

    def __str__(self):
        return '%s has %s' % (str(self.user), str(self.symptom))

    def getUser(self):
        return self.user

    def getUserName(self):
        return str(self.getUser())

    def getSymptomName(self):
        return str(self.symptom)


# Method Model
class Method(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    class Meta:
        verbose_name = 'Treatment'
        verbose_name_plural = 'Treatments'

    def __str__(self):
        return self.name

    # get user count use this method
    def getUsersByMethod(self, symptom_id, count=False):
        method_trials = UserMethodTrial.objects.filter(method=self)
        users = list(dict.fromkeys([method_trial.getUser()
                                    for method_trial in method_trials]))

        return len(users) if count else users

    # get user method trials
    def getMethodTrialsByMethod(self, count=False):
        method_trials = [method_trial for method_trial in UserMethodTrial.objects.filter(
            method__id=self.id)]

        method_trials = list(dict.fromkeys(method_trials))

        return len(method_trials) if count else method_trials

    # get Effectiveness score average
    def getAvgEffectivenessScore(self):
        method_trials = self.getMethodTrialsByMethod()
        scores = [method_trial.getEffectivenessScore()
                  for method_trial in method_trials]

        scores = [score for score in scores if score is not None]

        return mean(scores) if len(scores) else '-'

    # get Drawbacks score average
    def getAvgDrawbacksScore(self):
        method_trials = self.getMethodTrialsByMethod()
        scores = [method_trial.getDrawbacksScore()
                  for method_trial in method_trials]

        scores = [score for score in scores if score is not None]

        return mean(scores) if len(scores) else '-'


# User Severity Model
class UserSeverity(models.Model):
    severity = models.PositiveSmallIntegerField(choices=SEVERITIES, default=0)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateTimeField('date published', default=datetime.now)

    class Meta:
        verbose_name = 'Severity'
        verbose_name_plural = 'Severities'

    def __str__(self):
        return [severity[1] for severity in SEVERITIES if severity[0] == self.severity][0]

    def getScale(self):
        return self.severity


# User Method Trial Model
class UserMethodTrial(models.Model):
    user_symptom = models.ForeignKey(UserSymptom, on_delete=models.CASCADE)
    method = models.ForeignKey(Method, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'User treatment'
        verbose_name_plural = 'User treatments'
        unique_together = ['user_symptom', 'method']

    def __str__(self):
        return '%s used %s for %s' % (self.getUserName(), self.getMethodName(), self.getSymptomName())

    def getUser(self):
        return self.user_symptom.getUser()

    def getUserName(self):
        return self.user_symptom.getUserName()

    def getSymptomName(self):
        return self.user_symptom.getSymptomName()

    def getMethodName(self):
        return str(self.method)

    # get effectiveness score
    def getEffectivenessScore(self):
        start_severity = UserMethodTrialStartSeverity.objects.filter(
            user_method_trial=self)

        # TODO: start_severity must always exist - I think this means we need to change to the model
        if not len(start_severity):
            return None
        else:
            start_severity = start_severity[0]

        end_severity = UserMethodTrialEndSeverity.objects.filter(
            user_method_trial_start_severity=start_severity)

        # TODO: elseif there is a UserSeverityUpdate, use that as the "end_severity.getSeverity(False)
        if not len(end_severity):
            return None
        else:
            end_severity = end_severity[0]

        actual = end_severity.getSeverity(
            False) - start_severity.getSeverity(False)
        max_pos = 4 - start_severity.getSeverity(False)
        max_neg = -start_severity.getSeverity(False)

        return 100 * (actual - max_pos)/(max_neg - max_pos)

    # get Drawbacks score
    def getDrawbacksScore(self):
        start_severity = UserMethodTrialStartSeverity.objects.filter(
            user_method_trial=self)

        if not len(start_severity):
            return None
        else:
            start_severity = start_severity[0]

        end_severity = UserMethodTrialEndSeverity.objects.filter(
            user_method_trial_start_severity=start_severity)

        if not len(end_severity):
            return None
        else:
            end_severity = end_severity[0]

        actual = end_severity.getSeverity(
            False) - start_severity.getSeverity(False)
        max_pos = 4 - start_severity.getSeverity(False)
        max_neg = -start_severity.getSeverity(False)

        return 100 * (actual - max_neg)/(max_pos - max_neg)


# User Method Trial start severity
class UserMethodTrialStartSeverity(models.Model):
    user_method_trial = models.ForeignKey(
        UserMethodTrial, on_delete=models.CASCADE)
    severity = models.ForeignKey(UserSeverity, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Severity (start) of user treatment'
        verbose_name_plural = 'Severities (start) of user treatment'

    def __str__(self):
        return 'The start severity of %s (%s symptom) was %s' % (self.getUserName(), self.getSymptomName(), self.getSeverity())

    def getUserName(self):
        return self.user_method_trial.getUserName()

    def getSymptomName(self):
        return self.user_method_trial.getSymptomName()

    def getMethodName(self):
        return self.user_method_trial.getMethodName()

    def getSeverity(self, text=True):
        return str(self.severity) if text else self.severity.getScale()


# User Method Trial start severity
class UserMethodTrialEndSeverity(models.Model):
    user_method_trial_start_severity = models.ForeignKey(
        UserMethodTrialStartSeverity, on_delete=models.CASCADE)
    severity = models.ForeignKey(UserSeverity, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Severity (end) of user treatment'
        verbose_name_plural = 'Severities (end) of user treatment'

    def __str__(self):
        return '%s and finished with %s' % (str(self.user_method_trial_start_severity), self.getSeverity())

    def getUserName(self):
        return self.user_method_trial_start_severity.getUserName()

    def getSymptomName(self):
        return self.user_method_trial_start_severity.getSymptomName()

    def getMethodName(self):
        return self.user_method_trial_start_severity.getMethodName()

    def getStartSeverity(self, text=True):
        return self.user_method_trial_start_severity.getSeverity(text)

    def getSeverity(self, text=True):
        return str(self.severity) if text else self.severity.getScale()
