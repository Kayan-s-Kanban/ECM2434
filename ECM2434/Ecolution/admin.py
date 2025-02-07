from django.contrib import admin
from .models import User, Pet, Task, UserTask

# Register your models here.
admin.site.register(User)
admin.site.register(Pet)
admin.site.register(Task)
admin.site.register(UserTask)