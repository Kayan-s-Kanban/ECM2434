import uuid
import io
import qrcode
from django.db import models
from django.db.models import Q, F, Sum, Max
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # Best practice for referencing AUTH_USER_MODEL
from django.utils import timezone
from django.core.files.base import ContentFile
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

# ------------------------- CustomUser Model -------------------------
class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Includes additional fields for points, font size, displayed pet,
    and a flag for gamekeepers.
    """

    # Font size constants (in pixels)
    FONT_SIZE_SMALL = 13
    FONT_SIZE_MEDIUM = 16
    FONT_SIZE_LARGE = 19

    FONT_SIZE_CHOICES = [
        (FONT_SIZE_SMALL, 'Small'),
        (FONT_SIZE_MEDIUM, 'Medium'),
        (FONT_SIZE_LARGE, 'Large'),
    ]

    # Additional fields for CustomUser
    points = models.IntegerField(default=0)  # User's currency/points balance
    is_gamekeeper = models.BooleanField(default=False)  # True if the user is a gamekeeper
    preferred_font_size = models.PositiveSmallIntegerField(
        choices=FONT_SIZE_CHOICES,
        default=FONT_SIZE_MEDIUM,
    )
    displayed_pet = models.ForeignKey(
        'Pet',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='displayed_for'
    )

    @property
    def highest_pet_level(self):
        """
        Returns the highest pet level among the user's pets.
        If the user has no pets, returns 1.
        """
        result = self.pet_set.aggregate(max_level=Max('pet_level'))
        return result['max_level'] or 1

    def __str__(self):
        # Return the username when printing a CustomUser instance
        return f'{self.username}'

# ------------------------- Pet Model -------------------------
class Pet(models.Model):
    """
    Represents a pet owned by a user.
    A pet is a weak entity that depends on the existence of a user.
    """

    # Size constants and choices
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    SIZE_CHOICES = [
        (SMALL, 'Small'),
        (MEDIUM, 'Medium'),
        (LARGE, 'Large'),
    ]

    # Pet type constants and choices
    MUSHROOM = 'mushroom'
    ACORN = 'acorn'
    PLANT = 'plant'
    PET_CHOICES = [
        (MUSHROOM, 'Mushroom'),
        (ACORN, 'Acorn'),
        (PLANT, 'Plant'),
    ]

    # Foreign key to the owning user; cascade deletes the pet when the user is deleted
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Optional reference to a ShopItem for pet accessories (e.g., a hat)
    hat = models.ForeignKey('ShopItem', on_delete=models.SET_NULL, null=True, blank=True)
    pet_name = models.CharField(max_length=50)  # Display name for the pet
    pet_level = models.IntegerField(default=1)  # Level of the pet
    pet_exp = models.IntegerField(default=0)  # Experience points for the pet
    pet_type = models.CharField(max_length=10, choices=PET_CHOICES, default=MUSHROOM)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default=SMALL)

    def determine_size(self):
        """
        Determine the pet's size based on its level.
        Returns a size string.
        """
        if self.pet_level < 4:
            return self.SMALL
        elif 4 <= self.pet_level < 7:
            return self.MEDIUM
        else:
            return self.LARGE

    def save(self, *args, **kwargs):
        """
        Override the save() method to update the pet's size before saving.
        This avoids recalculating the size on every page load.
        """
        self.size = self.determine_size()
        super().save(*args, **kwargs)

    class Meta:
        # Ensure each user cannot have two pets with the same name
        unique_together = ('user', 'pet_name')
        # Constraint to ensure pet experience is within 0 and 100
        constraints = [
            models.CheckConstraint(
                check=models.Q(pet_exp__gte=0) & models.Q(pet_exp__lte=100),
                name='pet_exp_range'
            )
        ]

    @property
    def computed_image_url(self):
        """
        Construct and return the URL for the pet's image based on its type and size.
        """
        return f"/static/images/pets/{self.pet_type}/{self.pet_type}_{self.size}.gif"

    def __str__(self):
        # Return a string combining pet name and owner's username
        return f'{self.pet_name} - {self.user.username}'

# ------------------------- Event Model -------------------------
class Event(models.Model):
    """
    Represents an event created by a user (or gamekeeper).
    Each event can have associated tasks and generates a QR code for validation.
    """
    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=100)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    location = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    unique_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    url_qr_code = models.URLField(blank=True, null=True)  # Allows testing without scanning the QR code

    @property
    def total_points(self):
        """
        Calculate the total points given by all tasks associated with the event.
        """
        return self.task_set.aggregate(total=Sum('points_given'))['total'] or 0

    @property
    def total_xp(self):
        """
        Calculate the total XP given by all tasks associated with the event.
        """
        return self.task_set.aggregate(total=Sum('xp_given'))['total'] or 0

    def __str__(self):
        return f'{self.event_name}'

# Signal to generate a QR code for the event after it is saved
@receiver(post_save, sender=Event)
def generate_qr_code(sender, instance, created, **kwargs):
    """
    After saving an event, generate a QR code that contains a URL for event validation.
    This function updates the qr_code and url_qr_code fields without re-triggering the signal.
    """
    if created or not instance.qr_code:
        # Generate a relative URL for validating the QR code
        relative_url = reverse('validate_qr', kwargs={'token': instance.unique_token})
        full_url = f'https://ecolution.onrender.com{relative_url}'
        
        # Create a QR code using the qrcode library
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(full_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save the QR code image to a bytes buffer
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        # Generate a filename for the QR code image and save it to the model field
        file_name = f'event_{instance.pk}_qr.png'
        instance.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)
        instance.url_qr_code = full_url
        
        # Save only the updated QR code fields to avoid recursion in the post_save signal
        instance.save(update_fields=['qr_code', 'url_qr_code'])

# ------------------------- Task Model -------------------------
class Task(models.Model):
    """
    Represents a task that can be associated with an event.
    Tasks have point and XP rewards and may be predefined.
    """
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    points_given = models.IntegerField(default=500)
    xp_given = models.IntegerField(default=20)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    predefined = models.BooleanField(default=False)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, default=None, null=True, blank=True)

    class Meta:
        # Ensure that a creator cannot have two tasks with the same name
        constraints = [
            models.UniqueConstraint(
                fields=['task_name', 'creator'],
                name='unique_task_for_creator'
            )
        ]

    def __str__(self):
        return f'{self.task_name}'

# ------------------------- UserTask Model -------------------------
class UserTask(models.Model):
    """
    Represents a task assigned to a user.
    Tracks whether the user has completed the task on a specific date.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    date = models.DateField(default=timezone.now)

    class Meta:
        # Ensure a user can only have one record per task per day
        unique_together = ('user', 'task', 'date')

    def __str__(self):
        return f'{self.user.username} - {self.task.task_name}'

# ------------------------- UserEvent Model -------------------------
class UserEvent(models.Model):
    """
    Represents a user's participation in an event.
    Tracks whether the event is completed or validated.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    date = models.DateField(default=timezone.now)
    validated = models.BooleanField(default=False)

    class Meta:
        # Ensure a user can only join a particular event once per day
        unique_together = ('user', 'event', 'date')

    def __str__(self):
        return f'{self.user.username} - {self.event.event_name}'

# ------------------------- ShopItem Model -------------------------
class ShopItem(models.Model):
    """
    Represents an item available in the shop.
    Items have a price and may be used as accessories (e.g., hats).
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=5000)
    image_path = models.CharField(max_length=255, default='')  # Path to the item's image in static files
    is_hat = models.BooleanField(default=False)  # Flag to indicate if the item is a hat

    def __str__(self):
        return f'{self.name}'

# ------------------------- UserItem Model -------------------------
class UserItem(models.Model):
    """
    Represents an item owned by a user.
    Links a user to a ShopItem, ensuring that each user can only own one of each item.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shopitem = models.ForeignKey(ShopItem, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'shopitem')

    def __str__(self):
        return f'{self.user.username} - {self.shopitem.name}'
