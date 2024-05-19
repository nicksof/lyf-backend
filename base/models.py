from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver




# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profilePic = models.ImageField(null=True, blank=True)
    phoneNum = models.CharField(max_length=20, null=True, blank=True)
    streak = models.IntegerField()
    completedIA = models.BooleanField(null=True) #Remove null=True before deployment
    lastAssessment = models.CharField(max_length=50, null=True)

    def get_profilepic_url(self):
        if self.profilePic:
            return self.profilePic.url
        return None


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, streak=0, completedIA=False)


class Mood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.CharField(max_length=20)
    time = models.CharField(max_length=10)
    result = models.CharField(max_length=10)


class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    answer1 = models.CharField(max_length=100, null=True, blank=True)   
    answer2 = models.CharField(max_length=100, null=True, blank=True)
    answer3 = models.CharField(max_length=100, null=True, blank=True)
    answer4 = models.CharField(max_length=100, null=True, blank=True)
    answer5 = models.CharField(max_length=100, null=True, blank=True)

    hobby1 = models.CharField(max_length=50, null=True, blank=True)
    hobby2 = models.CharField(max_length=50, null=True, blank=True)
    hobby3 = models.CharField(max_length=50, null=True, blank=True)
    hobby4 = models.CharField(max_length=50, null=True, blank=True)

class Habit(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    habit1 = models.CharField(max_length=100, null=True, blank=True)   
    habit2 = models.CharField(max_length=100, null=True, blank=True)
    habit3 = models.CharField(max_length=100, null=True, blank=True)
    habit4 = models.CharField(max_length=100, null=True, blank=True)
    habit5 = models.CharField(max_length=100, null=True, blank=True)

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.CharField(max_length=20)
    habit1 = models.BooleanField(default=False)
    habit2 = models.BooleanField(default=False)
    habit3 = models.BooleanField(default=False)
    habit4 = models.BooleanField(default=False)
    habit5 = models.BooleanField(default=False)
    mood = models.BooleanField(default=False)

class HabitRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.CharField(max_length=20, null=True, blank=True)
    time = models.CharField(max_length=10, null=True, blank=True)
    habit = models.CharField(max_length=100, null=True, blank=True)

class Medication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medname = models.CharField(max_length=100)
    dosage = models.CharField(max_length=10)
    frequency = models.CharField(max_length=50)
    time = models.CharField(max_length=20)
    expiry = models.DateField(null=True, blank=True)

