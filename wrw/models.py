from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from statistics import mean
from datetime import datetime

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

        user_symptom = UserSymptom.objects.get(user=self, symptom=symptom)
        user_symptom_updates = UserSymptomUpdate.objects.filter(
            user_symptom=user_symptom).order_by('created_at')

        user_method_trial_starts = []
        if len(user_symptom_updates) > 1:
            user_method_trial_starts = UserMethodTrialStart.objects.filter(
                created_at__range=[
                    user_symptom_updates.first().getCreatedAt(),
                    user_symptom_updates.last().getCreatedAt()
                ])
        elif len(user_symptom_updates):
            user_method_trial_starts = UserMethodTrialStart.objects.filter(
                created_at=user_symptom_updates[0].getCreatedAt())
        else:
            return methods

        for user_method_trial_start in user_method_trial_starts:
            method = user_method_trial_start.getMethod()

            if method not in methods:
                methods.append(method)

        return methods

    # return data for side effect severity chart
    def getSideEffectSeverities(self):
        user_side_effect_updates = UserSideEffectUpdate.objects.filter(
            user=self).order_by('-created_at', '-id')

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
            user_symptom=user_symptom).order_by('-created_at', '-id')

        severities = [dict(
            title=user_symptom_update.getTitle(),
            description=user_symptom_update.getDescription(),
            severity=user_symptom_update.getSeverityRating(),
            created_at=user_symptom_update.getCreatedAt()
        ) for user_symptom_update in user_symptom_updates]

        return severities

    def getSymptomScore(self, symptom, method):
        user_method_trial_starts = UserMethodTrialStart.objects.filter(
            user=self, method=method)
        user_symptom = UserSymptom.objects.get(user=self, symptom=symptom)

        user_symptom_updates = []
        for user_method_trial_start in user_method_trial_starts:
            started_at = user_method_trial_start.getStartedAt()
            ended_at = user_method_trial_start.getEndedAt()

            if ended_at is None:
                ended_at = timezone.now()

            user_symptom_updates += UserSymptomUpdate.objects.filter(
                user_symptom=user_symptom, 
                created_at__range=[started_at, ended_at])

        if not user_symptom_updates:
            return None

        user_symptom_updates.sort(key=lambda x: x.getCreatedAt())

        start_severity = user_symptom_updates[0].getSeverityRating()
        end_severity = user_symptom_updates[-1].getSeverityRating()

        if start_severity is None or end_severity is None:
            return None

        try:
            actual = end_severity - start_severity
            max_pos = MAX_RATING - start_severity
            max_neg = -start_severity

            if actual == 0:
                return 0

            score = 100*actual/(max_neg if actual < 0 else -max_pos)

            return score
        except:
            return None

    def getSideEffectScore(self, symptom, method):
        user_method_trial_starts = UserMethodTrialStart.objects.filter(
            user=self, method=method)

        user_side_effect_updates = []
        for user_method_trial_start in user_method_trial_starts:
            started_at = user_method_trial_start.getStartedAt()
            ended_at = user_method_trial_start.getEndedAt()

            if ended_at is None:
                ended_at = timezone.now()

            user_side_effect_updates += UserSideEffectUpdate.objects.filter(
                created_at__range=[started_at, ended_at])

        if not user_side_effect_updates:
            return None

        user_side_effect_updates.sort(key=lambda x: x.getCreatedAt())

        start_severity = user_side_effect_updates[0].getSeverityRating()
        end_severity = user_side_effect_updates[-1].getSeverityRating()

        if start_severity is None or end_severity is None:
            return None

        try:
            actual = end_severity - start_severity
            max_pos = MAX_RATING - start_severity
            max_neg = -start_severity

            if actual == 0:
                return 0

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
                user_symptom=user_symptom).order_by('created_at')

            user_method_trial_starts = []
            if len(user_symptom_updates) > 1:
                user_method_trial_starts = UserMethodTrialStart.objects.filter(method=self, created_at__range=[
                    user_symptom_updates.first().getCreatedAt(),
                    user_symptom_updates.last().getCreatedAt()
                ])
            elif len(user_symptom_updates) == 1:
                user_method_trial_starts = UserMethodTrialStart.objects.filter(
                    method=self, created_at=user_symptom_updates[0].getCreatedAt())

            if len(user_method_trial_starts) and user_symptom.getUser() not in users:
                users.append(user_symptom.getUser())

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
            score = user.getSideEffectScore(symptom=symptom, method=self)

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
    created_at = models.DateTimeField('Created at', default=timezone.now)

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

    def getCreatedAt(self):
        return self.created_at


'''
/************************************************************
************* Method Trial Start
************************************************************/
'''


class UserMethodTrialStart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    method = models.ForeignKey(Method, on_delete=models.CASCADE)
    created_at = models.DateTimeField('Started at', default=timezone.now)

    class Meta:
        verbose_name = 'User Method Trial Start'
        verbose_name_plural = 'User Method Trial Starts'

    def __str__(self):
        return '%s : %s started at %s' % (self.user, self.getMethodName(), self.created_at)

    def getMethodName(self):
        return str(self.method)

    def getMethod(self):
        return self.method

    def getUserName(self):
        return str(self.user)

    def getStartedAt(self):
        return self.created_at

    def isEnded(self):
        try:
            user_method_trial_end = UserMethodTrialEnd.objects.get(
                user_method_trial_start=self)

            return True if user_method_trial_end else False
        except:
            return False

    def getEnded(self):
        if self.isEnded():
            user_method_trial_end = UserMethodTrialEnd.objects.get(
                user_method_trial_start=self)

            return user_method_trial_end

        return None

    def getEndedAt(self, default=None):
        user_method_trial_end = self.getEnded()

        return default if user_method_trial_end is None else user_method_trial_end.getEndedAt()

    def getStartedSymptomUpdate(self):
        try:
            return UserSymptomUpdate.objects.filter(user_method_trial_start=self, created_at=self.getStartedAt())[0]
        except:
            return None

    def getStartedSymptomSeverity(self):
        if self.getStartedSymptomUpdate() is not None:
            return self.getStartedSymptomUpdate().getSeverity()

        return None

    def getEndedSymptomUpdate(self):
        if self.isEnded():
            return UserSymptomUpdate.objects.filter(user_method_trial_start=self, created_at=self.getEndedAt())[0]

        return None

    def getEndedSymptomSeverity(self):
        if self.isEnded():
            return self.getEndedSymptomUpdate().getSeverity()

        return None

    def getStartedSideEffectUpdate(self):
        return UserSideEffectUpdate.objects.filter(user_method_trial_start=self, created_at=self.getStartedAt())[0]

    def getStartedSideEffectSeverity(self):
        return self.getStartedSideEffectUpdate().getSeverity()

    def getEndedSideEffectUpdate(self):
        if self.isEnded():
            return UserSideEffectUpdate.objects.filter(user_method_trial_start=self, created_at=self.getEndedAt())[0]

        return None

    def getEndedSideEffectSeverity(self):
        ended_side_effect_update = self.getEndedSideEffectUpdate()

        return ended_side_effect_update.getSeverity() if ended_side_effect_update else None

    def getTodaySymptomSeverity(self):
        user_symptom_updates = UserSymptomUpdate.objects.filter(user_method_trial_start=self, created_at__range=[
            datetime.combine(datetime.now(), datetime.min.time()),
            datetime.combine(datetime.now(), datetime.max.time())
        ]).order_by('created_at')

        return user_symptom_updates.last().getSeverity() if len(user_symptom_updates) else None

    def getTodaySideEffectUpdate(self):
        user_side_effect_updates = UserSideEffectUpdate.objects.filter(user_method_trial_start=self, created_at__range=[
            datetime.combine(datetime.now(), datetime.min.time()),
            datetime.combine(datetime.now(), datetime.max.time())
        ])

        return user_side_effect_updates.last() if len(user_side_effect_updates) else None

    def getTodaySideEffectSeverity(self):
        today_side_effect_update = self.getTodaySideEffectUpdate()

        return today_side_effect_update.getSeverity() if today_side_effect_update else None


'''
/************************************************************
************* Method Trial End
************************************************************/
'''


class UserMethodTrialEnd(models.Model):
    user_method_trial_start = models.OneToOneField(
        UserMethodTrialStart, on_delete=models.CASCADE)
    created_at = models.DateTimeField('Ended at', default=timezone.now)

    class Meta:
        verbose_name = 'User Method Trial End'
        verbose_name_plural = 'User Method Trial Ends'

    def __str__(self):
        return '%s ended at %s' % (self.user_method_trial_start, self.created_at)

    def getMethodName(self):
        return self.user_method_trial_start.getMethodName()

    def getUserName(self):
        return self.user_method_trial_start.getUserName()

    def getStartedAt(self):
        return self.user_method_trial_start.getStartedAt()

    def getEndedAt(self):
        return self.created_at


'''
/************************************************************
************* User Side Effect Update
************************************************************/
'''


class UserSideEffectUpdate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    side_effect_severity = models.ForeignKey(
        SideEffectSeverity, on_delete=models.CASCADE)
    user_method_trial_start = models.ForeignKey(
        UserMethodTrialStart, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField('Updated at', default=timezone.now)

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

    def getUserMethodTrialEnd(self):
        return self.user_method_trial_start.getEnded()


'''
/************************************************************
************* User Symptom Update
************************************************************/
'''


class UserSymptomUpdate(models.Model):
    user_symptom = models.ForeignKey(UserSymptom, on_delete=models.CASCADE)
    symptom_severity = models.ForeignKey(
        SymptomSeverity, on_delete=models.CASCADE)
    user_method_trial_start = models.ForeignKey(
        UserMethodTrialStart, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField('Updated at', default=timezone.now)

    class Meta:
        verbose_name = 'User Severity Update (Symptom)'
        verbose_name_plural = 'User Severity Updates (Symptom)'

    def getUserName(self):
        try:
            return self.user_symptom.getUserName()
        except ObjectDoesNotExist:
            return None
    getUserName.short_description = 'User Name'

    def getSymptomName(self):
        try:
            return self.user_symptom.getSymptomName()
        except ObjectDoesNotExist:
            return None
    getSymptomName.short_description = 'Symptom Name'

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
    getSeverityAsText.short_description = 'Severity'

    def getTitle(self):
        return self.title

    def getDescription(self):
        return self.description

    def getCreatedAt(self):
        return self.created_at

    def getUserMethodTrialEnd(self):
        return self.user_method_trial_start.getEnded()
