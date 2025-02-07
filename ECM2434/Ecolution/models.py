from django.db import models

# Create your models here.
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    points = models.IntegerField(default=0)
    #This changes the default display to username
    def __str__(self):
        return self.username
    

class Pet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pet_name = models.CharField(max_length=50)
    #This ensures that combinations of user and pet_name are unqiue
    class Meta:
        unique_together = ('user', 'pet_name')
    #This changes the default display to pet name and username
    def __str__(self):
        return f'{self.pet_name} - {self.user.username}'

class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=100)
    description = models.TextField()
    #This changes the default display to username
    def __str__(self):
        return self.task_name

class UserTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    #This ensures that combinations of user and task are unqiue
    class Meta:
        unique_together = ('user', 'task')
    #This changes the default display to username and task name
    def __str__(self):
        return f'{self.user.username} - {self.task.task_name}'