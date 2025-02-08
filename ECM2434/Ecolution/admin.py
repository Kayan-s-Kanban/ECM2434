from django.contrib import admin
from .models import Pet, Task, UserTask
from django.contrib.auth import get_user_model

User = get_user_model()

# Register your models here.
admin.site.register(Pet)
admin.site.register(Task)
admin.site.register(UserTask)