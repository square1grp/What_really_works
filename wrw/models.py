from django.db import models


class User(models.Model):
    name = models.CharField(max_length=20)
    
    def __str__(self):
        symptomName, methodName, startDate, endDate = "", "", "", ""

        symptomName = UserSymptom.objects.filter(user__id=self.id)[0].symptom.name if len(UserSymptom.objects.filter(user__id=self.id)) > 0 else ""

        userMethodTrial = UserMethodTrial.objects.filter(user__id=self.id)
        if len(userMethodTrial) > 0:
            userMethodTrial = userMethodTrial[0]
            methodName = userMethodTrial.method.name

            startDate = UserMethodTrialStartUpdate.objects.filter(user_method_trial__id = userMethodTrial.id)
            startDate = startDate[0].user_severity_update.date if len(startDate) > 0 else ""

            endDate = UserMethodTrialEndUpdate.objects.filter(user_method_trial__id = userMethodTrial.id)
            endDate = endDate[0].user_severity_update.date if len(endDate) > 0 else ""

        return "%s\n %s\n %s\n %s\n %s\n" % (self.name, symptomName, methodName, startDate, endDate)

    # get symptoms
    def getSymptoms(self):
        symptoms = []
        
        for user_symptom in UserSymptom.objects.filter(user__id=self.id):
            symptoms.append(user_symptom.symptom)
        
        return symptoms


class Symptom(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name


class Method(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name


class UserSymptom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.symptom)


class UserMethodTrial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    method = models.ForeignKey(Method, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.method


class UserSeverityUpdate(models.Model):
    user_symptom = models.ForeignKey(UserSymptom, on_delete=models.CASCADE)
    rating = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    date = models.DateTimeField('date published')
    
    def __str__(self):
        return self.title


class UserMethodTrialStartUpdate(models.Model):
    user_method_trial = models.ForeignKey(UserMethodTrial, on_delete=models.CASCADE)
    user_severity_update = models.ForeignKey(UserSeverityUpdate, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user_method_trial


class UserMethodTrialEndUpdate(models.Model):
    user_method_trial = models.ForeignKey(UserMethodTrial, on_delete=models.CASCADE)
    user_severity_update = models.ForeignKey(UserSeverityUpdate, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user_method_trial
        