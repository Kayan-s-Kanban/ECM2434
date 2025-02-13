from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Pet, Task, UserTask, Event, UserEvent
from django.contrib.auth import get_user_model
from .models import CustomUser
from .forms import CustomUserChangeForm

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'username', 'points',)

# Register your models here.
admin.site.register(Pet)
admin.site.register(Task)
admin.site.register(UserTask)
admin.site.register(Event)
admin.site.register(UserEvent)
admin.site.register(CustomUser, CustomUserAdmin)