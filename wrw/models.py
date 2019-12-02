from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from statistics import mean

RATING_CHOICES = [
    (0, 'None'),
    (1, 'Mild'),
    (2, 'Moderate'),
    (3, 'Severe'),
    (4, 'Very Severe')
]
MAX_RATING = 4


# convert rating (num to text, text to num, instance to any)
def convertRating(rating, to_text=True):
    try:
        if isinstance(rating, SymptomSeverity) or isinstance(rating, SideEffectSeverity):
            return rating.getSeverityAsText() if to_text else rating.getRating()

        if to_text:
            return [_rating[1] for _rating in RATING_CHOICES if _rating[0] == rating][0]

        return [_rating[0] for _rating in RATING_CHOICES if _rating[1] == rating][0]
    except:
        return rating


'''
/************************************************************
************* User
************************************************************/
'''


class User(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.name

    def getSymptoms(self):
        symptoms = []

        for user_symptom in UserSymptom.objects.filter(user=self):
            if user_symptom.symptom not in symptoms:
                symptoms.append(user_symptom.symptom)

        return symptoms

    def getMethodsBySymptom(self, symptom):
        methods = []

        for user_symptom in UserSymptom.objects.filter(user=self, symptom=symptom):
            user_symptom_updates = UserSymptomUpdate.objects.filter(
                user_symptom=user_symptom)

            for user_symptom in user_symptom_updates:
                method = user_symptom.getMethod()

                if method not in methods:
                    methods.append(method)

        return methods

    # return data for side effect severity chart
    def getSideEffectSeverities(self):
        user_side_effect_updates = UserSideEffectUpdate.objects.filter(
            user=self).order_by('-created_at')

        severities = [dict(
            title=user_side_effect_update.getTitle(),
            description=user_side_effect_update.getDescription(),
            severity=user_side_effect_update.getSeverityRating(),
            created_at=user_side_effect_update.getCreatedAt()
        ) for user_side_effect_update in user_side_effect_updates]

        return severities

    # return data for symptom severity chart
    def getSymptomSeverities(self, symptom):
        user_symptom = UserSymptom.objects.get(user=self, symptom=symptom)

        user_symptom_updates = UserSymptomUpdate.objects.filter(
            user_symptom=user_symptom).order_by('-created_at')

        severities = [dict(
            title=user_symptom_update.getTitle(),
            description=user_symptom_update.getDescription(),
            severity=user_symptom_update.getSeverityRating(),
            created_at=user_symptom_update.getCreatedAt()
        ) for user_symptom_update in user_symptom_updates]

        return severities

    def getSymptomScore(self, symptom, method):
        user_symptom = UserSymptom.objects.get(user=self, symptom=symptom)

        user_symptom_updates = UserSymptomUpdate.objects.filter(
            user_symptom=user_symptom,
            symptom_trial_start__method_trial_start__method=method,
            symptom_trial_end__method_trial_end__method=method).order_by('created_at')

        start_severity = user_symptom_updates.first().getSeverityRating()
        end_severity = user_symptom_updates.last().getSeverityRating()

        if start_severity is None or end_severity is None:
            return None

        try:
            actual = end_severity - start_severity
            max_pos = MAX_RATING - start_severity
            max_neg = -start_severity

            score = 100*actual/(max_neg if actual < 0 else -max_pos)

            return score
        except:
            return None

    def getSideEffectScore(self):
        user_side_effect_updates = UserSideEffectUpdate.objects.filter(
            user=self).order_by('created_at')

        start_severity = user_side_effect_updates.first().getSeverityRating()
        end_severity = user_side_effect_updates.last().getSeverityRating()

        if start_severity is None or end_severity is None:
            return None

        try:
            actual = end_severity - start_severity
            max_pos = MAX_RATING - start_severity
            max_neg = -start_severity

            score = 100*actual/(max_neg if actual < 0 else -max_pos)

            return score
        except:
            return None


'''
/************************************************************
************* Symptom
************************************************************/
'''


class Symptom(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Symptom'
        verbose_name_plural = 'Symptoms'

    def __str__(self):
        return self.name


'''
/************************************************************
************* Method
************************************************************/
'''


class Method(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Treatment'
        verbose_name_plural = 'Treatments'

    def __str__(self):
        return self.name

    # get users who started this method(self) for symptom provided
    def getUsersHaveSymptom(self, symptom):
        user_symptoms = UserSymptom.objects.filter(symptom=symptom)

        users = []
        for user_symptom in user_symptoms:
            user_symptom_updates = UserSymptomUpdate.objects.filter(
                user_symptom=user_symptom)

            for user_symptom_update in user_symptom_updates:
                if user_symptom_update.hasSymptomTrialStart() and user_symptom.user not in users:
                    users.append(user_symptom.user)

        return users

    def getSymptomScores(self, symptom):
        users = [user_symptom.user
                 for user_symptom in UserSymptom.objects.filter(symptom=symptom)]

        scores = []
        for user in users:
            score = user.getSymptomScore(symptom=symptom, method=self)

            if score is not None:
                scores.append(score)

        return scores

    def getAvgSymptomScore(self, symptom):
        scores = self.getSymptomScores(symptom)
        avg_score = round(mean(scores), 2) if len(scores) else ' - '

        return avg_score

    def getSideEffectScores(self, symptom):
        users = [user_symptom.user
                 for user_symptom in UserSymptom.objects.filter(symptom=symptom)]

        scores = []
        for user in users:
            score = user.getSideEffectScore()

            if score is not None:
                scores.append(score)

        return scores

    def getAvgSideEffectScore(self, symptom):
        scores = self.getSideEffectScores(symptom)
        avg_score = round(mean(scores), 2) if len(scores) else ' - '

        return avg_score


'''
/************************************************************
************* Symptom Severity
************************************************************/
'''


class SymptomSeverity(models.Model):
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, default=0)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Severity (Symptom)'
        verbose_name_plural = 'Severities (Symptom)'

    def __str__(self):
        return self.getSeverityAsText()

    # convert rating to the text human-readable
    def getSeverityAsText(self):
        return convertRating(self.rating, True)
    getSeverityAsText.short_description = 'Rating'

    def getRating(self):
        return self.rating

    def getDescription(self):
        return self.description


'''
/************************************************************
************* Side Effect Severity
************************************************************/
'''


class SideEffectSeverity(models.Model):
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, default=0)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Severity (Side Effect)'
        verbose_name_plural = 'Severities (Side Effect)'

    def __str__(self):
        return self.getSeverityAsText()

    # convert rating to the text human-readable
    def getSeverityAsText(self):
        return convertRating(self.rating, True)
    getSeverityAsText.short_description = 'Severity'

    def getRating(self):
        return self.rating

    def getDescription(self):
        return self.description


'''
/************************************************************
************* User Symptom
************************************************************/
'''


class UserSymptom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'User Symptom'
        verbose_name_plural = 'User Symptoms'

        unique_together = ['user', 'symptom']

    def __str__(self):
        return '%s : %s' % (self.getUserName(), self.getSymptomName())

    def getUserName(self):
        return str(self.user)

    def getUser(self):
        return self.user

    def getSymptomName(self):
        return str(self.symptom)


'''
/************************************************************
************* User Side Effect Update
************************************************************/
'''


class UserSideEffectUpdate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    side_effect_severity = models.ForeignKey(
        SideEffectSeverity, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateField('Updated at', default=timezone.now)

    class Meta:
        verbose_name = 'User Severity Update (Side Effect)'
        verbose_name_plural = 'User Severity Updates (Side Effect)'

    def __str__(self):
        return '%s : %s at %s' % (self.getUserName(), self.getSeverityAsText(), self.created_at)

    def getUserName(self):
        return str(self.user)

    def getSeverityAsText(self):
        try:
            return self.side_effect_severity.getSeverityAsText()
        except ObjectDoesNotExist:
            return None
    getSeverityAsText.short_description = 'Severity'

    def getSeverityRating(self):
        try:
            return self.side_effect_severity.getRating()
        except ObjectDoesNotExist:
            return None

    def getSeverity(self):
        try:
            return self.side_effect_severity
        except ObjectDoesNotExist:
            return None

    def getTitle(self):
        return self.title

    def getDescription(self):
        return self.description

    def getCreatedAt(self):
        return self.created_at


'''
/************************************************************
************* Method Trial Start
************************************************************/
'''


class MethodTrialStart(models.Model):
    method = models.ForeignKey(Method, on_delete=models.CASCADE)
    created_at = models.DateField('Started at', default=timezone.now)

    class Meta:
        verbose_name = 'Method Trial Start'
        verbose_name_plural = 'Method Trial Starts'

    def __str__(self):
        return '%s started at %s' % (self.getMethodName(), self.created_at)

    def getMethodName(self):
        return str(self.method)

    def getMethod(self):
        return self.method


'''
/************************************************************
************* Method Trial End
************************************************************/
'''


class MethodTrialEnd(models.Model):
    method = models.ForeignKey(Method, on_delete=models.CASCADE)
    created_at = models.DateField('Ended at', default=timezone.now)

    class Meta:
        verbose_name = 'Method Trial End'
        verbose_name_plural = 'Method Trial Ends'

    def __str__(self):
        return '%s ended at %s' % (self.getMethodName(), self.created_at)

    def getMethodName(self):
        return str(self.method)

    def getMethod(self):
        return self.method


'''
/************************************************************
************* Symptom Trial Start
************************************************************/
'''


class SymptomTrialStart(models.Model):
    method_trial_start = models.ForeignKey(
        MethodTrialStart, on_delete=models.CASCADE)
    created_at = models.DateField('Ended at', default=timezone.now)

    class Meta:
        verbose_name = 'Symptom Trial Start'
        verbose_name_plural = 'Symptom Trial Starts'

    def __str__(self):
        return 'Started at %s' % self.created_at

    def getMethodName(self):
        try:
            return self.method_trial_start.getMethodName()
        except ObjectDoesNotExist:
            return None

    def getMethod(self):
        try:
            return self.method_trial_start.getMethod()
        except ObjectDoesNotExist:
            return None

    def getStartedAt(self):
        return self.created_at


'''
/************************************************************
************* Symptom Trial End
************************************************************/
'''


class SymptomTrialEnd(models.Model):
    method_trial_end = models.ForeignKey(
        MethodTrialEnd, on_delete=models.CASCADE)
    symptom_trial_start = models.OneToOneField(
        SymptomTrialStart, on_delete=models.CASCADE)
    created_at = models.DateField('Ended at', default=timezone.now)

    class Meta:
        verbose_name = 'Symptom Trial End'
        verbose_name_plural = 'Symptom Trial Ends'

    def __str__(self):
        return '%s started at %s and ended at %s' % (self.getMethodName(), self.getStartedAt(), self.getEndedAt())

    def getMethodName(self):
        try:
            return self.method_trial_end.getMethodName()
        except ObjectDoesNotExist:
            return None

    def getMethod(self):
        try:
            return self.method_trial_end.getMethod()
        except ObjectDoesNotExist:
            return None

    def getStartedAt(self):
        try:
            return self.symptom_trial_start.getStartedAt()
        except ObjectDoesNotExist:
            return None

    def getEndedAt(self):
        return self.created_at


'''
/************************************************************
************* User Symptom Update
************************************************************/
'''


class UserSymptomUpdate(models.Model):
    user_symptom = models.ForeignKey(UserSymptom, on_delete=models.CASCADE)
    symptom_trial_start = models.ForeignKey(
        SymptomTrialStart, on_delete=models.CASCADE)
    symptom_trial_end = models.ForeignKey(
        SymptomTrialEnd, on_delete=models.CASCADE)
    symptom_severity = models.ForeignKey(
        SymptomSeverity, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateField('Updated at', default=timezone.now)

    class Meta:
        verbose_name = 'User Severity Update (Symptom)'
        verbose_name_plural = 'User Severity Updates (Symptom)'

    def hasSymptomTrialStart(self):
        __has_object = False

        try:
            __has_object = self.symptom_trial_start is not None
        except ObjectDoesNotExist:
            pass

        return __has_object

    def hasSymptomTrialEnd(self):
        __has_object = False

        try:
            __has_object = self.symptom_trial_end is not None
        except ObjectDoesNotExist:
            pass

        return __has_object

    def getUserName(self):
        try:
            return self.user_symptom.getUserName()
        except ObjectDoesNotExist:
            return None

    def getSymptomName(self):
        try:
            return self.user_symptom.getSymptomName()
        except ObjectDoesNotExist:
            return None

    def getSeverity(self):
        try:
            return self.symptom_severity
        except ObjectDoesNotExist:
            return None

    def getSeverityRating(self):
        try:
            return self.symptom_severity.getRating()
        except ObjectDoesNotExist:
            return None

    def getSeverityAsText(self):
        try:
            return self.symptom_severity.getSeverityAsText()
        except ObjectDoesNotExist:
            return None

    def getMethodName(self):
        try:
            return self.symptom_trial_start.getMethodName()
        except ObjectDoesNotExist:
            return None

    def getMethod(self):
        try:
            return self.symptom_trial_start.getMethod()
        except ObjectDoesNotExist:
            return None

    def getStartedAt(self, default=None):
        try:
            return self.symptom_trial_start.getStartedAt()
        except ObjectDoesNotExist:
            return default

    def getEndedAt(self, default=None):
        try:
            return self.symptom_trial_end.getEndedAt()
        except:
            return default

    def getTitle(self):
        return self.title

    def getDescription(self):
        return self.description

    def getCreatedAt(self):
        return self.created_at
