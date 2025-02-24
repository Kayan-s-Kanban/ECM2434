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

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('points',)}),
    )

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    # Show these fields in the list view (optional)
    list_display = ('task_name', 'creator', 'points_given', 'xp_given', 'event')
    
    # Show these fields in the edit form (and in this order)
    fields = ('task_name', 'creator', 'points_given', 'xp_given', 'event')
    
    # If you want a search box or filtering:
    search_fields = ('task_name',)
    list_filter = ('creator',)


# Register your models here.
admin.site.register(Pet)
admin.site.register(UserTask)
admin.site.register(Event)
admin.site.register(UserEvent)
admin.site.register(CustomUser, CustomUserAdmin)