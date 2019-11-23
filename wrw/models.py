from django.db import models
from django.utils import timezone


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


# ======================================================
# ======== Symptom Model
# ======================================================
class Symptom(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

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
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Treatment'
        verbose_name_plural = 'Treatments'

    def __str__(self):
        return self.name


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

    def getDescription(self):
        return self.description


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

    def getDescription(self):
        return self.description


# ======================================================
# ======== UserMethodTrialStart Model
# ======================================================
class UserMethodTrialStart(models.Model):
    method = models.ForeignKey(Method, on_delete=models.CASCADE)
    drawback = models.ForeignKey(Drawback, on_delete=models.CASCADE, default=0)
    created_at = models.DateField('Started at', default=timezone.now)

    class Meta:
        verbose_name = 'User Treatment Trial (start)'
        verbose_name_plural = 'User Treatment Trials (start)'

    def __str__(self):
        return '%s was started at %s' % (self.getMethodName(), self.created_at())

    def getMethodName(self):
        return str(self.method)

    getMethodName.short_description = 'Treatment'
    getMethodName.admin_order_field = 'method__name'

    def getDrawback(self):
        return self.drawback.getRatingText()

    getDrawback.short_description = 'Drawback'


# ======================================================
# ======== UserSymptomTrialStart Model
# ======================================================
class UserSymptomTrialStart(models.Model):
    user_method_trial_start = models.ForeignKey(
        UserMethodTrialStart, on_delete=models.CASCADE)
    severity = models.ForeignKey(Severity, on_delete=models.CASCADE, default=0)

    class Meta:
        verbose_name = 'User Treatment Trial (start)'
        verbose_name_plural = 'User Treatment Trials (start)'

    def __str__(self):
        return '%s and severity was %s' % (self.user_method_trial_start, self.getSeverity())

    def getMethodName(self):
        return self.user_method_trial_start.getMethodName()

    def getSeverity(self):
        return self.severity.getRatingText()

    getSeverity.short_description = 'Severity'

    def getDrawback(self):
        return self.user_method_trial_start.getDrawback()

    getDrawback.short_description = 'Drawback'


# ======================================================
# ======== UserMethodTrialEnd Model
# ======================================================
class UserMethodTrialEnd(models.Model):
    user_method_trial_start = models.OneToOneField(
        UserMethodTrialStart, on_delete=models.CASCADE)
    drawback = models.ForeignKey(Drawback, on_delete=models.CASCADE, default=0)
    created_at = models.DateField('Ended at', default=timezone.now)

    class Meta:
        verbose_name = 'User Treatment Trial (end)'
        verbose_name_plural = 'User Treatment Trials (end)'

    def __str__(self):
        return '%s and ended at %s' % (self.user_method_trial_start, self.created_at)

    def getMethodName(self):
        return self.user_method_trial_start.getMethodName()

    getMethodName.short_description = 'Treatment'
    getMethodName.admin_order_field = 'user_method_trial_start__method__name'

    def getDrawback(self):
        return self.drawback.getRatingText()

    getDrawback.short_description = 'Drawback'


# ======================================================
# ======== UserSymptomTrialEnd Model
# ======================================================
class UserSymptomTrialEnd(models.Model):
    user_symptom_trial_start = models.OneToOneField(
        UserSymptomTrialStart, on_delete=models.CASCADE)
    user_method_trial_end = models.ForeignKey(
        UserMethodTrialEnd, on_delete=models.CASCADE)
    severity = models.ForeignKey(Severity, on_delete=models.CASCADE, default=0)

    class Meta:
        verbose_name = 'User Treatment Trial (start)'
        verbose_name_plural = 'User Treatment Trials (start)'

    def __str__(self):
        return '%s : %s and severity was %s' % (self.user_symptom_trial_start, self.user_method_trial_end, self.getSeverity())

    def getMethodName(self):
        return self.user_method_trial_end.getMethodName()

    def getSeverity(self):
        return self.severity.getRatingText()

    getSeverity.short_description = 'Severity'

    def getDrawback(self):
        return self.user_symptom_trial_end.getDrawback()

    getDrawback.short_description = 'Drawback'


# ======================================================
# ======== UserSymptom Model
# ======================================================
class UserSymptom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    user_symptom_trial_start = models.ForeignKey(
        UserSymptomTrialStart, on_delete=models.CASCADE)
    user_symptom_trial_end = models.ForeignKey(
        UserSymptomTrialEnd, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'User Symptom'
        verbose_name_plural = 'User Symptoms'

        unique_together = ['user', 'symptom', 'user_symptom_trial_start']

    def __str__(self):
        return '''
            Username : %s, Symptom: %s
            %s
        ''' % (self.getUserName, self.getSymptomName(), self.user_symptom_trial_end if self.user_symptom_trial_end else self.user_symptom_trial_start)

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

    def getStartSeverity(self):
        return self.user_symptom_trial_start.getSeverity()

    getStartSeverity.short_description = 'Start Severity'

    def getStartDrawback(self):
        return self.user_symptom_trial_start.getDrawback()

    getStartDrawback.short_description = 'Start Drawback'

    def getEndSeverity(self):
        return self.user_symptom_trial_end.getSeverity() if self.user_symptom_trial_end else ' - '

    getEndSeverity.short_description = 'End Severity'

    def getEndDrawback(self):
        return self.user_symptom_trial_end.getDrawback() if self.user_symptom_trial_end else ' - '

    getEndDrawback.short_description = 'End Drawback'


# ======================================================
# ======== UserSymptomUpdate Model
# ======================================================
class UserSymptomUpdate(models.Model):
    user_symptom = models.ForeignKey(UserSymptom, on_delete=models.CASCADE)
    severity = models.ForeignKey(Severity, on_delete=models.CASCADE, default=0)
    drawback = models.ForeignKey(Drawback, on_delete=models.CASCADE, default=0)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateField('Updated at', default=timezone.now)

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

    def getDrawback(self):
        return self.drawback.getRatingText()

    getDrawback.short_description = 'Drawback'
