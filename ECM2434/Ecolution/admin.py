from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Pet, Task, UserTask, Event, UserEvent, ShopItem, UserItem
from django.contrib.auth import get_user_model
from .models import CustomUser
from .forms import CustomUserChangeForm

# Get the currently active User model (which in this case is our CustomUser)
User = get_user_model()

# Define a custom admin class for our CustomUser model that extends the default UserAdmin
class CustomUserAdmin(UserAdmin):
    # Use our custom form for both adding and changing user instances
    add_form = CustomUserChangeForm
    form = CustomUserChangeForm    
    model = CustomUser
    # Specify which fields are displayed in the list view for users in the admin panel
    list_display = ('email', 'username', 'points', 'preferred_font_size', 'displayed_pet', 'highest_pet_level', 'is_gamekeeper')
    
    # Extend the default fieldsets to include custom fields
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('points', 'preferred_font_size', 'displayed_pet', 'is_gamekeeper')}),
    )

    # Configure the fields that appear when adding a new user via the admin site
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

# Register all models with the Django admin site
admin.site.register(Pet)
admin.site.register(Task)
admin.site.register(UserTask)
admin.site.register(Event)
admin.site.register(UserEvent)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ShopItem)
admin.site.register(UserItem)
