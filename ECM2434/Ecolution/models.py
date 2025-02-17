from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # Best practice for referencing AUTH_USER_MODEL
from django.utils import timezone

class CustomUser(AbstractUser):  # ✅ Custom User model extending Django's built-in User
    points = models.IntegerField(default=0)  # Keeps your custom points field

    def __str__(self):
        return self.username

class Pet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Dynamic reference
    pet_name = models.CharField(max_length=50)
    pet_level = models.IntegerField(default=1)
    pet_exp = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'pet_name')
        constraints = [
            models.CheckConstraint(
                check=models.Q(pet_level__gte=1) & models.Q(pet_level__lte=10),
                name='pet_level_range'
            )
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(pet_exp__gte=0) & models.Q(pet_exp__lte=10),
                name='pet_exp_range'
            )
        ]

    def __str__(self):
        return f'{self.pet_name} - {self.user.username}'

class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=100)
    description = models.TextField()
    points_given = models.IntegerField(default=500)
    #xp_given = models.IntegerField(default=100)
    predefined = models.BooleanField(default=False)
    def __str__(self):
        return self.task_name

class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=100)
    description = models.TextField()
    def __str__(self):
        return self.event_name

class UserTask(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Dynamic reference
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'task', 'date')

    def __str__(self):
        return f'{self.user.username} - {self.task.task_name}'

class UserEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Dynamic reference
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event', 'date_time')

    def __str__(self):
        return f'{self.user.username} - {self.event.event_name}'
