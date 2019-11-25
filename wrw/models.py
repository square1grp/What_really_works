from django.db import models
from django.utils import timezone
from statistics import mean


RATING_CHOICES = [
    (0, 'None'),
    (1, 'Mild'),
    (2, 'Moderate'),
    (3, 'Severe'),
    (4, 'Very Severe')
]

MAX_RATING = 4


def convertRating(rating, to_text=True):
    try:
        if isinstance(rating, Severity):
            return rating.getRatingText() if to_text else rating.getRating()

        if to_text:
            return [_rating[1] for _rating in RATING_CHOICES if _rating[0] == rating][0]

        return [_rating[0] for _rating in RATING_CHOICES if _rating[1] == rating][0]
    except:
        return None


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
        symptoms = []

        for user_symptom in UserSymptom.objects.filter(user=self):
            if user_symptom.symptom not in symptoms:
                symptoms.append(user_symptom.symptom)

        return symptoms

    # get all symptom trials
    def getAllSymptomTrialsStarted(self):
        all_symptom_trials = []

        for user_symptom in UserSymptom.objects.filter(user=self):
            symptom = user_symptom.getSymptomName()
            user_symptom_trial_started = user_symptom.getTrialStarted()

            if user_symptom_trial_started is None:
                continue

            method = user_symptom_trial_started.getMethodName()
            started_at = user_symptom.getStartedAt()
            ended_at = user_symptom.getEndedAt()
            ended_at = ended_at if ended_at is not None else timezone.now().date()
            annotation_at = started_at+(ended_at-started_at)/2

            all_symptom_trials.append(
                dict(symptom=symptom,
                     method=method,
                     severity=user_symptom.getStartSeverity(),
                     started_at=started_at,
                     ended_at=ended_at,
                     annotation_at=annotation_at))

        return all_symptom_trials

    # get methods by symptom
    def getMethodsBySymptom(self, symptom):
        symptom = Symptom.objects.get(
            id=symptom) if isinstance(symptom, int) else symptom

        methods = []
        for user_symptom in UserSymptom.objects.filter(user=self, symptom=symptom):
            user_symptom_trial_started = user_symptom.getTrialStarted()

            if user_symptom_trial_started is None:
                continue

            method = user_symptom_trial_started.getMethod()

            if method not in methods:
                methods.append(method)

        return methods

    # get all severity updates
    def getAllSeverityUpdatesBySymptom(self, symptom):
        user_symptoms = UserSymptom.objects.filter(user=self, symptom=symptom)

        if not len(user_symptoms):
            return dict(effectivenesses=None, drawbacks=None)

        effectivenesses, drawbacks = [], []
        for user_symptom in user_symptoms:
            if user_symptom.has_user_symptom_trial_start():
                effectivenesses.append(dict(
                    title='No Title',
                    description='No Description',
                    severity=convertRating(user_symptom.getStartSeverity(), False),
                    created_at=user_symptom.getStartedAt()
                ))

                drawbacks.append(dict(
                    title='No Title',
                    description='No Description',
                    severity=convertRating(user_symptom.getStartDrawback(), False),
                    created_at=user_symptom.getStartedAt()
                ))

            if user_symptom.has_user_symptom_trial_end():
                effectivenesses.append(dict(
                    title='No Title',
                    description='No Description',
                    severity=convertRating(
                        user_symptom.getEndSeverity(), False),
                    created_at=user_symptom.getEndedAt()
                ))

                drawbacks.append(dict(
                    title='No Title',
                    description='No Description',
                    severity=convertRating(
                        user_symptom.getEndDrawback(), False),
                    created_at=user_symptom.getEndedAt()
                ))

            user_symptom_updates = UserSymptomUpdate.objects.filter(
                user_symptom=user_symptom)

            effectivenesses += [dict(
                title=user_symptom_update.title,
                description=user_symptom_update.description,
                severity=convertRating(
                    user_symptom_update.getSeverity(), False),
                created_at=user_symptom_update.getCreatedAt()
            ) for user_symptom_update in user_symptom_updates]

            drawbacks += [dict(
                title=user_symptom_update.title,
                description=user_symptom_update.description,
                severity=convertRating(
                    user_symptom_update.getDrawback(), False),
                created_at=user_symptom_update.getCreatedAt()
            ) for user_symptom_update in user_symptom_updates]

        effectivenesses.sort(key=lambda x: x['created_at'])
        drawbacks.sort(key=lambda x: x['created_at'])

        return dict(effectivenesses=effectivenesses, drawbacks=drawbacks)


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

    # get Effectiveness score average
    # get Drawback score average
    def getAverageScore(self, symptom, is_effectiveness=True):
        symptom = Symptom.objects.get(
            id=symptom) if isinstance(symptom, int) else symptom
        user_symptoms = UserSymptom.objects.filter(
            symptom=symptom, user_symptom_trial_start__user_method_trial_start__method=self)
        scores = [(user_symptom.getEffectivenessScore() if is_effectiveness else user_symptom.getDrawbackScore())
                  for user_symptom in user_symptoms]

        scores = [score for score in scores if score is not None]

        avg_score = round(mean(scores), 2) if len(scores) else '-'

        return avg_score

    def getUsersHaveSymptom(self, symptom):
        symptom = Symptom.objects.get(
            id=symptom) if isinstance(symptom, int) else symptom

        user_symptoms = UserSymptom.objects.filter(
            symptom=symptom, user_symptom_trial_start__user_method_trial_start__method=self)

        return [user_symptom.user for user_symptom in user_symptoms]

    def getStatistics(self, symptom):
        symptom = Symptom.objects.get(
            id=symptom) if isinstance(symptom, int) else symptom

        user_symptoms = UserSymptom.objects.filter(
            symptom=symptom, user_symptom_trial_start__user_method_trial_start__method=self)

        statistics_data = (
            [user_symptom.getEffectivenessScore()
             for user_symptom in user_symptoms],
            [user_symptom.getDrawbackScore() for user_symptom in user_symptoms]
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
        return convertRating(self.rating, True)

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
        return convertRating(self.rating, True)

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
        return '%s was started at %s' % (self.getMethodName(), self.created_at)

    def getMethodName(self):
        return str(self.method)

    getMethodName.short_description = 'Treatment'
    getMethodName.admin_order_field = 'method__name'

    def getMethod(self):
        return self.method

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
        verbose_name = 'User Symptom Trial (start)'
        verbose_name_plural = 'User Symptom Trials (start)'

    def __str__(self):
        return '%s and severity was %s' % (self.user_method_trial_start, self.getSeverity())

    def getMethodName(self):
        return self.user_method_trial_start.getMethodName()

    getMethodName.short_description = 'Treatment'

    def getMethod(self):
        return self.user_method_trial_start.getMethod()

    def getSeverity(self):
        return self.severity.getRatingText()

    getSeverity.short_description = 'Severity'

    def getDrawback(self):
        return self.user_method_trial_start.getDrawback()

    getDrawback.short_description = 'Drawback'

    def getStartedAt(self):
        return self.user_method_trial_start.created_at


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
        return 'ended at %s' % self.created_at

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
        verbose_name = 'User Symptom Trial (end)'
        verbose_name_plural = 'User Symptom Trials (end)'

    def __str__(self):
        return '%s, %s and severity was %s' % (self.user_symptom_trial_start, self.user_method_trial_end, self.getSeverity())

    def getMethodName(self):
        return self.user_method_trial_end.getMethodName()

    getMethodName.short_description = 'Treatment'

    def getSeverity(self):
        return self.severity.getRatingText()

    getSeverity.short_description = 'Severity'

    def getDrawback(self):
        return self.user_method_trial_end.getDrawback()

    getDrawback.short_description = 'Drawback'

    def getStartedAt(self):
        return self.user_symptom_trial_start.getStartedAt()

    def getEndedAt(self):
        return self.user_method_trial_end.created_at


# ======================================================
# ======== UserSymptom Model
# ======================================================
class UserSymptom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    user_symptom_trial_start = models.ForeignKey(
        UserSymptomTrialStart, on_delete=models.CASCADE, blank=True, null=True)
    user_symptom_trial_end = models.ForeignKey(
        UserSymptomTrialEnd, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateField(
        'Started at', default=timezone.now, blank=True, null=True)

    class Meta:
        verbose_name = 'User Symptom'
        verbose_name_plural = 'User Symptoms'

        unique_together = ['user', 'symptom']

    def has_user_symptom_trial_start(self):
        __has_object = False

        try:
            __has_object = self.user_symptom_trial_start is not None
        except UserSymptomTrialStart.DoesNotExist:
            pass

        return __has_object

    def has_user_symptom_trial_end(self):
        __has_object = False

        try:
            __has_object = self.user_symptom_trial_end is not None
        except UserSymptomTrialEnd.DoesNotExist:
            pass

        return __has_object

    def __str__(self):
        return '''
            (Username : %s, Symptom: %s)
            %s
        ''' % (
            self.getUserName(),
            self.getSymptomName(),
            self.user_symptom_trial_end if self.has_user_symptom_trial_end() else (
                self.user_symptom_trial_start if self.has_user_symptom_trial_start() else ''
            )
        )

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

    def getTrialStarted(self):
        return self.user_symptom_trial_start if self.has_user_symptom_trial_start() else None

    def getStartSeverity(self):
        return self.user_symptom_trial_start.getSeverity() if self.has_user_symptom_trial_start() else None

    getStartSeverity.short_description = 'Start Severity'

    def getStartDrawback(self):
        return self.user_symptom_trial_start.getDrawback() if self.has_user_symptom_trial_start() else None

    getStartDrawback.short_description = 'Start Drawback'

    def getTrialEnded(self):
        return self.user_symptom_trial_end if self.has_user_symptom_trial_end() else None

    def getStartedAt(self):
        return self.user_symptom_trial_start.getStartedAt() if self.has_user_symptom_trial_start() else None

    def getEndedAt(self):
        return self.user_symptom_trial_end.getEndedAt() if self.has_user_symptom_trial_end() else None

    # get last symptom update
    def getLastSymptomUpdate(self):
        user_symptom_updates = UserSymptomUpdate.objects.filter(
            user_symptom=self).order_by('-created_at')

        user_symptom_updates = [
            user_symptom_update for user_symptom_update in user_symptom_updates if user_symptom_update.created_at > self.getStartedAt()]

        if not len(user_symptom_updates):
            return None

        user_symptom_update = user_symptom_updates[0]

        return user_symptom_update

    def getUserSymptomTrialEndOthers(self):
        user_symptom_trial_end_others = []

        user_symptoms = [user_symptom for user_symptom in UserSymptom.objects.filter(
            user=self.user, symptom=self.symptom) if user_symptom.has_user_symptom_trial_end()]

        for user_symptom in user_symptoms:
            if user_symptom.user_symptom_trial_end not in user_symptom_trial_end_others:
                user_symptom_trial_end_others.append(
                    user_symptom.user_symptom_trial_end)

        return user_symptom_trial_end_others

    def getEndSeverity(self, for_score=False):
        if not for_score:
            return self.user_symptom_trial_end.getSeverity() if self.user_symptom_trial_end else ' - '

        if self.has_user_symptom_trial_end():
            return convertRating(self.user_symptom_trial_end.getSeverity(), False)

        last_symptom_update = self.getLastSymptomUpdate()

        user_symptom_trial_end_others = self.getUserSymptomTrialEndOthers()
        if len(user_symptom_trial_end_others):
            user_symptom_trial_end = user_symptom_trial_end_others.pop(0)

            for _user_symptom_trial_end in user_symptom_trial_end_others:
                if _user_symptom_trial_end.getEndedAt() > user_symptom_trial_end.getEndedAt():
                    user_symptom_trial_end = _user_symptom_trial_end

            if last_symptom_update is None:
                return convertRating(user_symptom_trial_end.getSeverity(), False)

            if last_symptom_update.created_at > user_symptom_trial_end.getEndedAt():
                return convertRating(last_symptom_update.getSeverity(), False)

            return convertRating(user_symptom_trial_end.getSeverity(), False)

        if last_symptom_update is not None:
            return convertRating(last_symptom_update.getSeverity(), False)
        else:
            return None

    getEndSeverity.short_description = 'End Severity'

    def getEndDrawback(self, for_score=False):
        if not for_score:
            return self.user_symptom_trial_end.getDrawback() if self.user_symptom_trial_end else ' - '

        if self.has_user_symptom_trial_end():
            return convertRating(self.user_symptom_trial_end.getDrawback(), False)

        last_symptom_update = self.getLastSymptomUpdate()

        user_symptom_trial_end_others = self.getUserSymptomTrialEndOthers()
        if len(user_symptom_trial_end_others):
            user_symptom_trial_end = user_symptom_trial_end_others.pop(0)

            for _user_symptom_trial_end in user_symptom_trial_end_others:
                if _user_symptom_trial_end.getEndedAt() > user_symptom_trial_end.getEndedAt():
                    user_symptom_trial_end = _user_symptom_trial_end

            if last_symptom_update is None:
                return convertRating(user_symptom_trial_end.getDrawback(), False)

            if last_symptom_update.created_at > user_symptom_trial_end.getEndedAt():
                return convertRating(last_symptom_update.getDrawback(), False)

            return convertRating(user_symptom_trial_end.getDrawback(), False)

        if last_symptom_update is not None:
            return convertRating(last_symptom_update.getDrawback(), False)
        else:
            return None

    getEndDrawback.short_description = 'End Drawback'

    # get effectiveness score
    def getEffectivenessScore(self):
        start_severity = convertRating(
            self.user_symptom_trial_start.getSeverity(), False) if self.has_user_symptom_trial_start() else None

        if start_severity is None:
            return None

        end_severity = self.getEndSeverity(True)

        if end_severity is None:
            return None

        actual = end_severity - start_severity
        max_pos = MAX_RATING - start_severity
        max_neg = -start_severity

        if (actual < 0):
            score = 100 * actual / max_neg
        else:
            score = -100 * actual / max_pos

        return round(score, 2)

    # get drawback score
    def getDrawbackScore(self):
        start_drawback = convertRating(
            self.user_symptom_trial_start.getDrawback(), False) if self.has_user_symptom_trial_start() else None

        if start_drawback is None:
            return None

        end_drawback = self.getEndDrawback(True)

        if end_drawback is None:
            return None

        actual = end_drawback - start_drawback
        max_pos = MAX_RATING - start_drawback
        max_neg = -start_drawback

        if (actual < 0):
            score = 100 * actual / max_neg
        else:
            score = -100 * actual / max_pos

        return round(score, 2)

    def getCreatedAt(self):
        created_at = None

        try:
            created_at = self.created_at
        except models.DateField.DoesNotExist:
            created_at = ''

        return created_at


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

    def getCreatedAt(self):
        return self.created_at
