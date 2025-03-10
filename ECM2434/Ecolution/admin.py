from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Pet, Task, UserTask, Event, UserEvent, ShopItem, UserItem
from django.contrib.auth import get_user_model
from .models import CustomUser
from .forms import CustomUserChangeForm

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserChangeForm
    form = CustomUserChangeForm    
    model = CustomUser
    list_display = ('email', 'username', 'points', 'preferred_font_size', 'displayed_pet')

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('points', 'preferred_font_size', 'displayed_pet')}),
    )

    # This controls what fields appear when adding a NEW user:
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email',
                'points', 'preferred_font_size',
                'password',
            ),
        }),
    )

# Register your models here.
admin.site.register(Pet)
admin.site.register(Task)
admin.site.register(UserTask)
admin.site.register(Event)
admin.site.register(UserEvent)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ShopItem)
admin.site.register(UserItem)