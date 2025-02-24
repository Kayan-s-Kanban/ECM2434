from django.db import models
from django.db.models import Q, F, Sum
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # Best practice for referencing AUTH_USER_MODEL
from django.utils import timezone

class CustomUser(AbstractUser):  # ✅ Custom User model extending Django's built-in User
    
    FONT_SIZE_SMALL = 13
    FONT_SIZE_MEDIUM = 16
    FONT_SIZE_LARGE = 19

    FONT_SIZE_CHOICES = [
        (FONT_SIZE_SMALL, 'Small'),
        (FONT_SIZE_MEDIUM, 'Medium'),
        (FONT_SIZE_LARGE, 'Large'),
    ]
    points = models.IntegerField(default=0)  # Keeps your custom points field
    preferred_font_size = models.PositiveSmallIntegerField(
        choices=FONT_SIZE_CHOICES,
        default=FONT_SIZE_MEDIUM,
    )

    def __str__(self):
        return self.username

class Pet(models.Model):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'

    SIZE_CHOICES = [
        (SMALL, 'Small'),
        (MEDIUM, 'Medium'),
        (LARGE, 'Large'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Dynamic reference
    pet_name = models.CharField(max_length=50)
    pet_level = models.IntegerField(default=1)
    pet_exp = models.IntegerField(default=0)
    pet_type = models.CharField(max_length=50, default='mushroom')  # e.g., 'dragon', 'mushroom', 'cat'
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default=SMALL)

    def determine_size(self):
        """Sets the pet size based on its level."""
        if self.pet_level < 4:
            return self.SMALL
        elif 4 <= self.pet_level < 7:
            return self.MEDIUM
        else:
            return self.LARGE

    def save(self, *args, **kwargs):
        """Automatically updates the size before saving."""
        self.size = self.determine_size()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'pet_name')
        constraints = [
            models.CheckConstraint(
                check=models.Q(pet_level__gte=1) & models.Q(pet_level__lte=10),
                name='pet_level_range'
            ),
            models.CheckConstraint(
                check=models.Q(pet_exp__gte=0) & models.Q(pet_exp__lte=100 + (F('pet_level') * 20)),
                name='pet_exp_range'
            )
        ]

    def __str__(self):
        return f'{self.pet_name} - {self.user.username}'

class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100, blank=True)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)

    @property
    def total_points(self):
        # Assuming a reverse relation name of 'task_set' or something else if you specified `related_name`.
        return self.task_set.aggregate(total=Sum('points_given'))['total'] or 0

    def __str__(self):
        return self.event_name
    
class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=100)
    description = models.TextField()
    points_given = models.IntegerField(default=500)
    xp_given = models.IntegerField(default=20)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, default=None, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['task_name', 'creator'],
                name='unique_task_for_creator'
            )
        ]

    def __str__(self):
        return self.task_name


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
    date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'event', 'date')

    def __str__(self):
        return f'{self.user.username} - {self.event.event_name}'
