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

class CustomUser(AbstractUser):  # Custom User model is the user class we use for base users and super users
    
    FONT_SIZE_SMALL = 13 #custom data type for font size takes px and converts them to english words
    FONT_SIZE_MEDIUM = 16
    FONT_SIZE_LARGE = 19

    FONT_SIZE_CHOICES = [
        (FONT_SIZE_SMALL, 'Small'),
        (FONT_SIZE_MEDIUM, 'Medium'),
        (FONT_SIZE_LARGE, 'Large'),
    ]
    points = models.IntegerField(default=0)  # the points field
    preferred_font_size = models.PositiveSmallIntegerField( #stores the preferred font size also has a default so that the size of the text exists when a usr is not logged in 
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
        result = self.pet_set.aggregate(max_level=Max('pet_level'))
        return result['max_level'] or 1

    def __str__(self): #function that returns username
        return f'{self.username}'

class Pet(models.Model): #weak entity pet that relies on user id to exist
    SMALL = 'small' #custom data field used for describing size of pets
    MEDIUM = 'medium'
    LARGE = 'large'

    SIZE_CHOICES = [
        (SMALL, 'Small'),
        (MEDIUM, 'Medium'),
        (LARGE, 'Large'),
    ]
    MUSHROOM = 'mushroom' #custom data field used for describing type of pet
    ACORN = 'acorn'
    PLANT = 'plant'

    PET_CHOICES = [
        (MUSHROOM, 'Mushroom'),
        (ACORN, 'Acorn'),
        (PLANT, 'Plant'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # since pets is a weak entity when the user is deleted the pet is also deleted thats what cascade does
    pet_name = models.CharField(max_length=50) #pet name used in the display on the home page
    pet_level = models.IntegerField(default=1) # pet level used to determine size and is displayed on the home page
    pet_exp = models.IntegerField(default=0) #pet exp used to determine when a pet should level up also displayed on the home page
    pet_type = models.CharField(max_length=10, choices=PET_CHOICES, default=MUSHROOM)  # pet type used in the home page to create the file path to where the image of the pets are
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default=SMALL) #size is also used when creating the file path to find the pets 

    def determine_size(self): #used to update the size of the pets based on the level of them
        """Sets the pet size based on its level."""
        if self.pet_level < 4:
            return self.SMALL
        elif 4 <= self.pet_level < 7:
            return self.MEDIUM
        else:
            return self.LARGE

    def save(self, *args, **kwargs): #used to update the size data item so deterine size isnt constantly used when opening th ehome page
        """Automatically updates the size before saving."""
        self.size = self.determine_size()
        super().save(*args, **kwargs)

    class Meta: #used to set constraints on the pet level and pet exp
        unique_together = ('user', 'pet_name')
        constraints = [
            models.CheckConstraint(
                check=models.Q(pet_exp__gte=0) & models.Q(pet_exp__lte=100),
                name='pet_exp_range'
            )
        ]
    
    @property # generate image url for the pet
    def computed_image_url(self):
        return f"/static/images/pets/{self.pet_type}/{self.pet_type}_{self.size}.gif" # Might need to change this or the determine size so it updates on changes
    
    def __str__(self):
        return f'{self.pet_name} - {self.user.username}'

class Event(models.Model): 
    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100, blank=True)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    unique_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    url_qr_code = models.URLField(blank=True, null=True) # This field is here to allow me to test the view without currently needing to scan the QR Code

    @property
    def total_points(self):
        return self.task_set.aggregate(total=Sum('points_given'))['total'] or 0
    
    @property
    def total_xp(self):
        return self.task_set.aggregate(total=Sum('xp_given'))['total'] or 0

    def __str__(self):
        return f'{self.event_name}'
    
# This signal will run after an Event is saved.
@receiver(post_save, sender=Event)
def generate_qr_code(sender, instance, created, **kwargs):
    # If the Event is new or if for some reason the QR code hasn't been generated
    if created or not instance.qr_code:
        # Generate the relative URL using reverse()
        relative_url = reverse('validate_qr', kwargs={'token': instance.unique_token})
        full_url = f'http://127.0.0.1:8000/{relative_url}'
        
        # Create the QR code image using the qrcode library.
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(full_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save the image to a bytes buffer.
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        # Create a filename that includes the event's primary key.
        file_name = f'event_{instance.pk}_qr.png'
        # Save the generated image without calling save() on the model immediately
        instance.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)
        instance.url_qr_code = full_url
        
        # Update only the QR code fields to avoid re-triggering the creation logic.
        instance.save(update_fields=['qr_code', 'url_qr_code'])
        
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
        return f'{self.task_name}'


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
    validated = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'event', 'date')

    def __str__(self):
        return f'{self.user.username} - {self.event.event_name}'
    
class ShopItem(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=5000)
    image_path = models.CharField(max_length=255, default='') # haven't added a default image path yet

    def __str__(self):
        return f'{self.name}'

class UserItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Dynamic reference
    shopitem = models.ForeignKey(ShopItem, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'shopitem')

    def __str__(self):
        return f'{self.user.username} - {self.shopitem.name}'
    
class GameKeeper(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Dynamic reference

    def __str__(self):
        return f'{self.user.username} - GameKeeper'
