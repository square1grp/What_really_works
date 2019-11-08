from django.db import models
from datetime import datetime
from statistics import *


class User(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    # get symptoms
    def getSymptoms(self):
        symptoms = []

        for user_symptom in UserSymptom.objects.filter(user__id=self.id):
            symptoms.append(user_symptom.symptom)

        return symptoms

    # get methods
    def getMethods(self, no_duplicate=True):
        methods = [method_trial.method for method_trial in UserMethodTrial.objects.filter(
            user__id=self.id)]

        if no_duplicate:
            return list(dict.fromkeys(methods))

        return methods


class Symptom(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name


class Method(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

    # get user count use this method
    def getUsersByMethod(self, symptom_id, count=False):
        users = [method_trial.user for method_trial in UserMethodTrial.objects.filter(
            method__id=self.id)]

        user_ids = [user.id for user in UserSymptom.getUsersBySymptom(symptom_id)]
        users = [user for user in users if user.id in user_ids]
        
        users = list(dict.fromkeys(users))

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

        return mean(scores) if len(scores) else '#'

    # get Drawbacks score average
    def getAvgDrawbacksScore(self):
        method_trials = self.getMethodTrialsByMethod()
        scores = [method_trial.getDrawbacksScore()
                  for method_trial in method_trials]

        scores = [score for score in scores if score is not None]

        return mean(scores) if len(scores) else '#'


class UserSymptom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.symptom)

    @staticmethod
    def getUsersBySymptom(symptom_id):
        users = []

        for symptom in UserSymptom.objects.filter(symptom__id=symptom_id):
            users.append(symptom.user)

        return users


class UserMethodTrial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    method = models.ForeignKey(Method, on_delete=models.CASCADE)

    def __str__(self):
        return '%s - %s' % (str(self.user), str(self.method))

    # get effectiveness score
    def getEffectivenessScore(self):
        try:
            start_severity = UserMethodTrialStartUpdate.objects.filter(
                user_method_trial__id=self.id)[0]
            end_severity = UserMethodTrialEndUpdate.objects.filter(
                user_method_trial_start_severity__id=start_severity.id)

            if not len(end_severity):
                return None

            end_severity = end_severity[0]

            actual = end_severity.user_severity_update.rating - \
                start_severity.user_severity_update.rating
            max_pos = 4 - start_severity.user_severity_update.rating
            max_neg = -start_severity.user_severity_update.rating

            return 100 * (actual - max_pos)/(max_neg - max_pos)

        except:
            return None

    # get Drawbacks score
    def getDrawbacksScore(self):
        try:
            start_severity = UserMethodTrialStartUpdate.objects.filter(
                user_method_trial__id=self.id)[0]
            end_severity = UserMethodTrialEndUpdate.objects.filter(
                user_method_trial_start_severity__id=start_severity.id)

            if not len(end_severity):
                return None

            end_severity = end_severity[0]

            actual = end_severity.user_severity_update.rating - \
                start_severity.user_severity_update.rating
            max_pos = 4 - start_severity.user_severity_update.rating
            max_neg = -start_severity.user_severity_update.rating

            return 100 * (actual - max_neg)/(max_pos - max_neg)

        except:
            return None


class UserSeverityUpdate(models.Model):
    user_symptom = models.ForeignKey(UserSymptom, on_delete=models.CASCADE)
    rating = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateTimeField('date published', default=datetime.now)

    def __str__(self):
        return '%s - %s - %s' % (str(self.user_symptom.symptom), self.title, self.date)


class UserMethodTrialStartUpdate(models.Model):
    user_method_trial = models.ForeignKey(
        UserMethodTrial, on_delete=models.CASCADE)
    user_severity_update = models.ForeignKey(
        UserSeverityUpdate, on_delete=models.CASCADE)

    def __str__(self):
        return '%s : %s' % (str(self.user_method_trial), str(self.user_severity_update))


class UserMethodTrialEndUpdate(models.Model):
    user_method_trial_start_severity = models.ForeignKey(
        UserMethodTrialStartUpdate, on_delete=models.CASCADE, null=True)
    user_severity_update = models.ForeignKey(
        UserSeverityUpdate, on_delete=models.CASCADE)

    def __str__(self):
        return '%s to %s' % (str(self.user_method_trial_start_severity), self.user_severity_update.title)
