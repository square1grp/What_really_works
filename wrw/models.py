from django.db import models
from datetime import datetime
from statistics import mean


RATING_CHOICES = [
    (0, 'None'),
    (1, 'Mild'),
    (2, 'Moderate'),
    (3, 'Severe'),
    (4, 'Very Severe')
]

MAX_RATING = 4


# ======================================================
# ======== User Model
# ======================================================
class User(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.name

    # get all symptoms that the current user has
    def getSymptoms(self):
        symptoms = [
            user_symptom.symptom for user_symptom in UserSymptom.objects.filter(user=self)]

        return symptoms

    # get all methods that the current user started for symptom provided
    def getMethodsBySymptom(self, symptom):
        symptom = Symptom.objects.get(
            id=symptom) if isinstance(symptom, int) else symptom
        user_symptom = UserSymptom.objects.filter(user=self, symptom=symptom)

        if not len(user_symptom):
            return []

        user_symptom = user_symptom[0]

        methods = [user_method_trial_start.method for user_method_trial_start in UserMethodTrialStart.objects.filter(
            user_symptom=user_symptom)]

        return methods

    # get all method trials started
    def getAllMethodTrialsStarted(self):
        all_method_trials = []

        for method_trial_start in UserMethodTrialStart.objects.filter(user_symptom__user=self).order_by('created_at'):
            method = method_trial_start.getMethodName()
            started_at = method_trial_start.created_at.astimezone(tz=None)
            method_trial_end = UserMethodTrialEnd.objects.filter(
                user_method_trial_start=method_trial_start).first()
            ended_at = datetime.now().astimezone(tz=None)
            if method_trial_end is not None:
                ended_at = method_trial_end.created_at.astimezone(tz=None)

            annotation_at = started_at+(ended_at-started_at)/2

            all_method_trials.append(
                dict(method=method,
                     severity=method_trial_start.getSeverity(),
                     started_at=started_at.strftime('%Y-%m-%d %H:%M:%S'),
                     ended_at=ended_at.strftime('%Y-%m-%d %H:%M:%S'),
                     annotation_at=annotation_at.strftime('%Y-%m-%d %H:%M:%S')))

        return all_method_trials

    # get all severity updates
    def getAllSeverityUpdatesBySymptom(self, symptom):
        user_symptom = UserSymptom.objects.filter(user=self, symptom=symptom)

        if not len(user_symptom):
            return dict(effectivenesses=None, drawbacks=None)

        user_symptom = user_symptom[0]

        user_method_trials_started = []
        user_method_trials_ended = []
        user_symptom_updates = []

        for user_method_trial_started in UserMethodTrialStart.objects.filter(user_symptom=user_symptom):
            user_method_trials_started.append(user_method_trial_started)

            user_method_trials_ended += UserMethodTrialEnd.objects.filter(
                user_method_trial_start=user_method_trial_started)

        user_symptom_updates += UserSymptomUpdate.objects.filter(
            user_symptom=user_symptom)

        severity_data = (user_method_trials_started +
                         user_method_trials_ended + user_symptom_updates)
        severity_data.sort(key=lambda x: x.created_at)

        effectivenesses = [dict(severity=data.severity.getRating(), created_at=data.created_at.strftime(
            '%Y-%m-%d %H:%M:%S'), title=data.severity.title) for data in severity_data]
        drawbacks = [dict(severity=data.drawback.getRating(), created_at=data.created_at.strftime(
            '%Y-%m-%d %H:%M:%S'), title=data.drawback.title) for data in severity_data]

        return dict(effectivenesses=effectivenesses, drawbacks=drawbacks)


# ======================================================
# ======== Symptom Model
# ======================================================
class Symptom(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    class Meta:
        verbose_name = 'Symptom'
        verbose_name_plural = 'Symptoms'

    def __str__(self):
        return self.name


# ======================================================
# ======== Method Model
# ======================================================
class Method(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    class Meta:
        verbose_name = 'Treatment'
        verbose_name_plural = 'Treatments'

    def __str__(self):
        return self.name

    # get all started user method trials with the current method
    def getStartedUserMethodTrials(self, symptom):
        started_user_method_trials = UserMethodTrialStart.objects.filter(
            method=self, user_symptom__symptom=symptom)

        return started_user_method_trials

    # get Effectiveness score average
    def getAvgEffectivenessScore(self, symptom):
        started_user_method_trials = self.getStartedUserMethodTrials(symptom)
        scores = [started_user_method_trial.getEffectivenessScore()
                  for started_user_method_trial in started_user_method_trials]

        scores = [score for score in scores if score is not None]

        avg_score = round(mean(scores), 2) if len(scores) else '-'

        return avg_score

    # get Drawback score average
    def getAvgDrawbackScore(self, symptom):
        started_user_method_trials = self.getStartedUserMethodTrials(symptom)
        scores = [started_user_method_trial.getDrawbackScore()
                  for started_user_method_trial in started_user_method_trials]

        scores = [score for score in scores if score is not None]

        avg_score = round(mean(scores), 2) if len(scores) else '-'

        return avg_score

    # get users by method, symptom
    def getUsersHaveSymptom(self, symptom):
        started_user_method_trials = self.getStartedUserMethodTrials(symptom)
        users = [started_user_method_trial.getUser()
                 for started_user_method_trial in started_user_method_trials]

        return users

    def getStatistics(self, symptom):
        started_user_method_trials = self.getStartedUserMethodTrials(symptom)

        statistics_data = (
            [started_user_method_trial.getEffectivenessScore()
             for started_user_method_trial in started_user_method_trials],
            [started_user_method_trial.getDrawbackScore()
             for started_user_method_trial in started_user_method_trials]
        )

        return statistics_data


# ======================================================
# ======== Severity Model
# ======================================================
class Severity(models.Model):
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, default=0)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Severity'
        verbose_name_plural = 'Severities'

    def __str__(self):
        return self.getRatingText()

    # convert rating to the text human-readable
    def getRatingText(self):
        return [rating[1] for rating in RATING_CHOICES if rating[0] == self.rating][0]

    getRatingText.short_description = 'Rating'

    def getRating(self):
        return self.rating


# ======================================================
# ======== Drawback Model
# ======================================================
class Drawback(models.Model):
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, default=0)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Drawback'
        verbose_name_plural = 'Drawbacks'

    def __str__(self):
        return self.getRatingText()

    # convert rating to the text human-readable
    def getRatingText(self):
        return [rating[1] for rating in RATING_CHOICES if rating[0] == self.rating][0]

    getRatingText.short_description = 'Rating'

    def getRating(self):
        return self.rating


# ======================================================
# ======== UserSymptom Model
# ======================================================
class UserSymptom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'User Symptom'
        verbose_name_plural = 'User Symptoms'

        unique_together = ['user', 'symptom']

    def __str__(self):
        return '%s : %s' % (str(self.user), str(self.symptom))

    def getUserName(self):
        return str(self.user)

    getUserName.short_description = 'User'
    getUserName.admin_order_field = 'user__name'

    def getUser(self):
        return self.user

    def getSymptomName(self):
        return str(self.symptom)

    getSymptomName.short_description = 'Symptom'
    getSymptomName.admin_order_field = 'symptom__name'

    def getSymptom(self):
        return self.symptom


# ======================================================
# ======== UserSymptomUpdate Model
# ======================================================
class UserSymptomUpdate(models.Model):
    user_symptom = models.ForeignKey(UserSymptom, on_delete=models.CASCADE)
    severity = models.ForeignKey(Severity, on_delete=models.CASCADE, default=0)
    drawback = models.ForeignKey(Drawback, on_delete=models.CASCADE, default=0)
    created_at = models.DateTimeField('Updated at', default=datetime.now)

    class Meta:
        verbose_name = 'User Symptom Update'
        verbose_name_plural = 'User Symptoms Update'

    def __str__(self):
        return '%s - %s : %s' % (self.user_symptom.getUserName(),
                                 self.user_symptom.getSymptomName(),
                                 self.severity.getRatingText())

    def getUserName(self):
        return self.user_symptom.getUserName()

    getUserName.short_description = 'User'
    getUserName.admin_order_field = 'user_symptom__user__name'

    def getSymptomName(self):
        return self.user_symptom.getSymptomName()

    getSymptomName.short_description = 'Symptom'
    getSymptomName.admin_order_field = 'user_symptom__symptom__name'

    def getSeverity(self):
        return self.severity.getRatingText()

    getSeverity.short_description = 'Severity'


# ======================================================
# ======== UserMethodTrialStart Model
# ======================================================
class UserMethodTrialStart(models.Model):
    user_symptom = models.ForeignKey(UserSymptom, on_delete=models.CASCADE)
    method = models.ForeignKey(Method, on_delete=models.CASCADE)
    severity = models.ForeignKey(Severity, on_delete=models.CASCADE, default=0)
    drawback = models.ForeignKey(Drawback, on_delete=models.CASCADE, default=0)
    created_at = models.DateTimeField('Started at', default=datetime.now)

    class Meta:
        verbose_name = 'User Treatment Trial (begin)'
        verbose_name_plural = 'User Treatment Trials (begin)'

    def __str__(self):
        return '%s - %s : %s' % (self.user_symptom.getUserName(),
                                 self.user_symptom.getSymptomName(),
                                 self.severity.getRatingText())

    def getUserName(self):
        return self.user_symptom.getUserName()

    getUserName.short_description = 'User'
    getUserName.admin_order_field = 'user_symptom__user__name'

    def getUser(self):
        return self.user_symptom.getUser()

    def getSymptom(self):
        return self.user_symptom.getSymptom()

    def getSymptomName(self):
        return str(self.getSymptom())

    getSymptomName.short_description = 'Symptom'
    getSymptomName.admin_order_field = 'user_symptom__symptom__name'

    def getMethodName(self):
        return str(self.method)

    getMethodName.short_description = 'Treatment'
    getMethodName.admin_order_field = 'method__name'

    def getSeverity(self):
        return self.severity.getRatingText()

    getSeverity.short_description = 'Severity'

    # get last symptom update
    def getLastSymptomUpdate(self):
        user_symptom_updates = UserSymptomUpdate.objects.filter(
            user_symptom=self.user_symptom).order_by('-created_at')

        user_symptom_updates = [
            user_symptom_update for user_symptom_update in user_symptom_updates if user_symptom_update.created_at > self.created_at]

        if not len(user_symptom_updates):
            return None

        user_symptom_update = user_symptom_updates[0]

        return user_symptom_update

    # get effectiveness score
    def getEffectivenessScore(self):
        start_severity = self.severity

        # user method trial end with this trial start
        user_method_trial_end = UserMethodTrialEnd.objects.filter(
            user_method_trial_start=self)

        # user method trial end under same symptom
        user_method_trial_end_others = UserMethodTrialEnd.objects.filter(
            user_method_trial_start__user_symptom__symptom=self.getSymptom()
        ).order_by('-created_at')

        # get last symptom update
        last_symptom_update = self.getLastSymptomUpdate()

        if len(user_method_trial_end):
            user_method_trial_end = user_method_trial_end[0]
            end_severity = user_method_trial_end.severity
        else:
            if len(user_method_trial_end_others):
                if user_method_trial_end_others[0].created_at > last_symptom_update.created_at or last_symptom_update is None:
                    end_severity = user_method_trial_end_others[0].severity
                elif last_symptom_update is not None:
                    end_severity = last_symptom_update.severity
                else:
                    return None
            elif last_symptom_update is not None:
                end_severity = last_symptom_update.severity
            else:
                return None

        actual = end_severity.getRating() - start_severity.getRating()
        max_pos = MAX_RATING - start_severity.getRating()
        max_neg = -start_severity.getRating()

        if (actual < 0):
            score = 100 * actual / max_neg
        else:
            score = -100 * actual / max_pos

        return round(score, 2)

    # get drawback score
    def getDrawbackScore(self):
        start_drawback = self.drawback

        # user method trial end with this trial start
        user_method_trial_end = UserMethodTrialEnd.objects.filter(
            user_method_trial_start=self)

        # user method trial end under same symptom
        user_method_trial_end_others = UserMethodTrialEnd.objects.filter(
            user_method_trial_start__user_symptom__symptom=self.getSymptom()
        ).order_by('-created_at')

        # get last symptom update
        last_symptom_update = self.getLastSymptomUpdate()

        if len(user_method_trial_end):
            user_method_trial_end = user_method_trial_end[0]
            end_drawback = user_method_trial_end.drawback
        else:
            if len(user_method_trial_end_others):
                if user_method_trial_end_others[0].created_at > last_symptom_update.created_at or last_symptom_update is None:
                    end_drawback = user_method_trial_end_others[0].drawback
                elif last_symptom_update is not None:
                    end_drawback = last_symptom_update.drawback
                else:
                    return None
            elif last_symptom_update is not None:
                end_drawback = last_symptom_update.drawback
            else:
                return None

        actual = end_drawback.getRating() - start_drawback.getRating()
        max_pos = MAX_RATING - start_drawback.getRating()
        max_neg = -start_drawback.getRating()

        if (actual < 0):
            score = 100 * actual / max_neg
        else:
            score = -100 * actual / max_pos

        return round(score, 2)


# ======================================================
# ======== UserMethodTrialEnd Model
# ======================================================
class UserMethodTrialEnd(models.Model):
    user_method_trial_start = models.OneToOneField(
        UserMethodTrialStart, on_delete=models.CASCADE)
    severity = models.ForeignKey(Severity, on_delete=models.CASCADE)
    drawback = models.ForeignKey(Drawback, on_delete=models.CASCADE)
    created_at = models.DateTimeField('Ended at', default=datetime.now)

    class Meta:
        verbose_name = 'User Treatment Trial (end)'
        verbose_name_plural = 'User Treatment Trials (end)'
