import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import logout, authenticate, login, get_user_model, update_session_auth_hash
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from .decorators import gamekeeper_required
from .models import Task, UserTask, CustomUser, Pet, Event, UserEvent, ShopItem, UserItem
from django.db.models import Max
from .decorators import gamekeeper_required
from django.utils import timezone

# Create your views here.

# Get the current User model (in this case, our CustomUser)
User = get_user_model()


def index(request):
    # Redirects to the home page.
    return redirect("home")


def signup_view(request):
    # Handles the user sign up process.
    if request.method == "POST":
        # Retrieve form fields.
        email = request.POST["email"]
        username = request.POST["username"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        pet_type = request.POST.get("pet_type", "mushroom")
        # Use the pet name provided, or default to the pet_type if not provided.
        pet_name = request.POST.get("pet_name", "") if pet_type else None

        # Validate the email using Django's built-in validator.
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return render(request, "signup.html")

        # Ensure the username is unique.
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('signup')

        # Ensure the passwords match.
        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return render(request, "signup.html")

        # Validate the password using Django's password validators.
        try:
            validate_password(password1)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, "signup.html")

        # Create the new user and save.
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        # Create a pet for the new user.
        pet = Pet.objects.create(user=user, pet_name=pet_name if pet_name else pet_type, pet_type=pet_type)
        pet.save()

        # Set the newly created pet as the user's displayed pet.
        user.displayed_pet = pet
        user.save()

        # Try to assign a shop item (hat) matching the pet type to the user.
        try:
            shop_item = ShopItem.objects.get(name__iexact=pet_type)
            UserItem.objects.create(user=user, shopitem=shop_item)
        except ShopItem.DoesNotExist:
            pass

        messages.success(request, "Account created! You can now log in.")
        return redirect("login")

    return render(request, "signup.html")


def login_view(request):
    print("DOES THIS FUCKING WORK")
    # Handles user login.
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        # Authenticate the user credentials.
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


@never_cache
def logout_view(request):
    # Logs out the current user and redirects to login page.
    logout(request)
    return redirect("login")


@login_required
def home_view(request):
    # Display the home page for the logged-in user.
    user = request.user
    pet = request.user.displayed_pet  # Get the pet that the user has chosen to display.
    # Retrieve the 5 most recent incomplete tasks for display.
    user_tasks = UserTask.objects.filter(user=user, completed=False).order_by('date')[:5]

    hat = pet.hat if pet and pet.hat else None

    # Context for rendering the home page template.
    context = {
        "points": user.points,
        "pet_exp": pet.pet_exp if pet else 0,
        "pet_name": pet.pet_name if pet else "No Pet",
        "pet_type": pet.pet_type.lower() if pet else "default",
        "pet_size": pet.determine_size() if pet else "small",  # Calculate pet size dynamically.
        "level": pet.pet_level if pet else 0,
        "pet": pet,
        "hat": hat,
        "user_tasks": user_tasks
    }
    return render(request, 'home.html', context)


@login_required
def tasks_view(request):
    """
    Renders the tasks page showing all tasks for the current user.
    Displays both predefined tasks (superuser-created) and custom tasks (user-created).
    """
    user_tasks = UserTask.objects.filter(user=request.user)
    predefined_tasks = Task.objects.filter(predefined=True)
    custom_tasks = Task.objects.filter(creator=request.user)
    return render(request, "tasks.html", {
        "user_tasks": user_tasks,
        "predefined_tasks": predefined_tasks,
        "custom_tasks": custom_tasks,
        "points": request.user.points
    })


@login_required
def add_task(request):
    """
    Adds a new task to the user's active task list.
    Can either add an existing task (predefined/custom) or create a new custom task.
    """
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        task_name = request.POST.get("task_name")
        description = request.POST.get("description")

        if task_id:
            # User selected an existing task.
            task = get_user_or_superuser_task(task_id, request.user)
        else:
            # User is creating a new custom task.
            if Task.objects.filter(creator=request.user, task_name=task_name).exists():
                return JsonResponse({
                    "status": "error",
                    "message": "You already created a custom task with that title."
                }, status=400)
            task = Task.objects.create(
                task_name=task_name,
                description=description,
                creator=request.user
            )

        try:
            # Try to add the task for the user.
            UserTask.objects.create(user=request.user, task=task)
        except IntegrityError:
            # IntegrityError occurs if the task already exists for the day.
            return JsonResponse({
                "status": "error",
                "message": "This task already exists!"
            }, status=400)

        return JsonResponse({
            "status": "success",
            "task_name": task.task_name,
            "description": task.description
        })

    return JsonResponse({"status": "error"}, status=400)


def get_user_or_superuser_task(task_id, user):
    """
    Returns a Task object based on task_id that either belongs to the current user
    or is a predefined (superuser-created) task.
    """
    try:
        return Task.objects.get(task_id=task_id, creator=user)
    except Task.DoesNotExist:
        pass

    try:
        return Task.objects.get(task_id=task_id, predefined=True)
    except Task.DoesNotExist:
        raise Http404("Task not found or not accessible.")


@login_required
def delete_task(request, user_task_id):
    # Deletes a UserTask instance.
    if request.method == "POST":
        user_task = get_object_or_404(UserTask, pk=user_task_id, user=request.user)
        user_task.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({"status": "error"}, status=400)


@login_required
def complete_task(request, task_id):
    # Marks a task as complete and awards points and XP.
    if request.method == "POST":
        user_task = get_object_or_404(UserTask, task__task_id=task_id, user=request.user)
        if not user_task.completed:
            user_task.completed = True
            user_task.save()

            # Update user's points.
            task = user_task.task
            request.user.points += task.points_given
            request.user.save()

            # Update pet's experience and level.
            pet = request.user.displayed_pet
            if pet:
                pet.pet_exp += task.xp_given
                while pet.pet_exp >= 100:
                    pet.pet_level += 1
                    pet.pet_exp -= 100
                pet.save()
        return JsonResponse({"status": "success", "points": request.user.points})
    return JsonResponse({"status": "error"}, status=400)


@login_required
def events_view(request):
    # Retrieves the events the user has joined and those available for joining.
    all_user_events = UserEvent.objects.filter(user=request.user)
    incomplete_user_events = UserEvent.objects.filter(user=request.user, completed=False)

    user_events = Event.objects.filter(event_id__in=incomplete_user_events.values_list("event_id", flat=True))
    all_events = Event.objects.exclude(event_id__in=all_user_events.values_list("event_id", flat=True))
    
    context = {"user_events": user_events, "events": all_events, "points": request.user.points}
    return render(request, "events.html", context)


@login_required
def join_event(request):
    # Handles joining an event.
    if request.method == "POST":
        try:
            event_id = request.POST.get("event_id")
            event = get_object_or_404(Event, event_id=event_id)
            UserEvent.objects.create(user=request.user, event=event)
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request"})


@login_required
def leave_event(request):
    # Handles leaving an event.
    if request.method == "POST":
        try:
            event_id = request.POST.get("event_id")
            event = get_object_or_404(Event, event_id=event_id)
            UserEvent.objects.filter(user=request.user, event=event).delete()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request"})


@login_required
def complete_event(request):
    # Marks an event as completed after validating via QR code.
    if request.method == "POST":
        try:
            event_id = request.POST.get("event_id")
            event = get_object_or_404(Event, event_id=event_id)
            user_event = get_object_or_404(UserEvent, user=request.user, event=event)
            
            # Ensure the event is validated (QR scanned)
            if not user_event.validated:
                return JsonResponse({"success": False, "message": "Event not validated. Please ask the event organiser for the QR code and go to the QR code scanner page."})
            
            # Award points based on event's total points.
            event_points = event.total_points
            CustomUser.objects.filter(id=request.user.id).update(points=request.user.points + event_points)
            
            # Update pet experience using event's total XP.
            event_xp = event.total_xp
            pet = request.user.displayed_pet
            if pet:
                pet.pet_exp += task.xp_given  # Note: This should likely be event_xp, not task.xp_given.
                while pet.pet_exp >= 100:
                    pet.pet_level += 1
                    pet.pet_exp -= 100
                pet.save()
            user_event.completed = True
            user_event.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request"})

@gamekeeper_required
@login_required
def create_event(request):
    # Allows gamekeepers to create new events along with associated tasks.
    if request.method == "POST":
        event_name = request.POST.get("event_name")
        description = request.POST.get("description")
        location = request.POST.get("location")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        date = request.POST.get("date")
        time = request.POST.get("time")
        task_names = request.POST.getlist("task_name")
        task_points = request.POST.getlist("task_points")
        task_xps = request.POST.getlist("task_xp")
        creator = request.user

        try:
            event = Event.objects.create(
                event_name=event_name,
                description=description,
                location=location,
                latitude=latitude,
                longitude=longitude,
                date=date,
                time=time,
                creator=creator,
            )

            # Create each task associated with the event.
            for name, points, xp in zip(task_names, task_points, task_xps):
                if name.strip():
                    Task.objects.create(
                        event=event,
                        task_name=name,
                        xp_given=int(xp),
                        points_given=int(points),
                        creator=creator
                    )

        except IntegrityError as e:
            return JsonResponse({"status": "error", "message": "Database Integrity Error: " + str(e)}, status=400)
    
        return redirect("gamekeeper_events") 

    return JsonResponse({"status": "error"}, status=400)
    

@login_required
def get_event_tasks(request, event_id):
    # Retrieves tasks for a given event.
    try:    
        event = get_object_or_404(Event, event_id=event_id)
        tasks = Task.objects.filter(event=event)

        tasks_data = [
            {
                "task_id": task.task_id,
                "task_name": task.task_name,
                "description": task.description,
                "points_given": task.points_given,
                "xp_given": task.xp_given,
            }
            for task in tasks
        ]

        return JsonResponse({"tasks": tasks_data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@gamekeeper_required
@login_required
def gamekeeper_events(request):
    gamekeeper_events = Event.objects.filter(creator=request.user)
    context = {"gamekeeper_events": gamekeeper_events}
    return render(request, "gamekeeper_events.html", context)


def settings_view(request):
    # Renders the settings page with the user's name and points.
    user = request.user
    context = {
        "name": user.username,
        "points": user.points
    }
    return render(request, "settings.html", context)


@login_required
def delete_account(request):
    # Deletes the current user's account and all associated data.
    user = request.user

    if request.method == "POST":
        # Delete all related UserTask, UserEvent, and Pet objects.
        UserTask.objects.filter(user=user).delete()
        UserEvent.objects.filter(user=user).delete()
        Pet.objects.filter(user=user).delete()

        # Delete the user account.
        user.delete()
        logout(request)
        messages.success(request, "Your account has been deleted successfully.")
        return redirect("home")  # Change "home" to your homepage URL name

    return render(request, "delete_account.html")


@login_required
def change_password(request):
    # Allows the user to change their password.
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password1 = request.POST["new_password1"]
        new_password2 = request.POST["new_password2"]

        user = request.user
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect!")
            return render(request, "settings.html")
        
        if new_password1 != new_password2:
            messages.error(request, "Passwords do not match!")
            return render(request, "settings.html")

        try:
            validate_password(new_password1)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, "settings.html")

        user.set_password(new_password1)
        user.save()
        update_session_auth_hash(request, user)  # Keep user logged in after password change.
        messages.success(request, "Password updated successfully!")
        return render(request, "settings.html")

    return redirect("settings")


@login_required
def change_username(request):
    # Allows the user to change their username.
    if request.method == "POST":
        new_username1 = request.POST["new_username1"]
        new_username2 = request.POST["new_username2"]
        
        if new_username1 != new_username2:
            messages.error(request, "New usernames do not match. Please choose another")
            return redirect("settings")

        user = request.user
        # Check if the new username is already taken.
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(username=new_username1).exists():
            messages.error(request, "This username is already taken!")
            return redirect("settings")

        user.username = new_username1
        user.save()
        update_session_auth_hash(request, user)  # Keep the user logged in.
        messages.success(request, "Username updated successfully!")
        return redirect("settings")

    return redirect("settings")


@login_required
def update_fontsize(request):
    # Updates the user's preferred font size.
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            try:
                font_size = int(data.get("preferred_font_size"))
            except (TypeError, ValueError):
                return JsonResponse({"status": "error", "message": "Invalid font size"})

            if font_size not in [CustomUser.FONT_SIZE_SMALL, CustomUser.FONT_SIZE_MEDIUM, CustomUser.FONT_SIZE_LARGE]:
                return JsonResponse({"status": "error", "message": "Invalid font size"})

            request.user.preferred_font_size = font_size
            request.user.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid request"})


@login_required
def get_fontsize(request):
    # Returns the user's preferred font size as JSON.
    return JsonResponse({"preferred_font_size": request.user.preferred_font_size})


def terms_view(request):
    # Renders the terms and conditions page.
    return render(request, "term.html")


@login_required
def shop_view(request):
    # Displays the shop items, along with items the user has purchased.
    shop_items = ShopItem.objects.all()
    purchased_item_ids = UserItem.objects.filter(user=request.user).values_list('shopitem__id', flat=True)
    return render(request, "shop.html", {
        "shop_items": shop_items,
        "purchased_item_ids": list(purchased_item_ids),
        "points": request.user.points
    })


@login_required
def buy_item(request, item_id):
    # Handles purchasing an item from the shop.
    if request.method == "POST":
        shop_item = get_object_or_404(ShopItem, id=item_id)
        if UserItem.objects.filter(user=request.user, shopitem=shop_item).exists():
            return JsonResponse({
                "status": "error",
                "message": "You have already purchased this item."
            }, status=400)
        
        if request.user.points < shop_item.price:
            return JsonResponse({
                "status": "error",
                "message": "Insufficient points to purchase this item."
            }, status=400)
        
        # Deduct the item's price from the user's points.
        request.user.points -= shop_item.price
        request.user.save()
        UserItem.objects.create(user=request.user, shopitem=shop_item)

        # If the shop item is a pet accessory (hat), create a pet for the user.
        if shop_item.name.lower() in ['mushroom', 'acorn', 'plant']:
            pet = Pet.objects.create(
                user=request.user,
                pet_name=shop_item.name,
                pet_type=shop_item.name.lower()
            )

        return JsonResponse({
            "status": "success",
            "message": "Purchase successful!",
            "item": shop_item.name,
            "remaining_points": request.user.points
        })
    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)


@login_required
def cycle_pet(request):
    # Cycles through the user's pets and updates the displayed pet.
    user = request.user
    pets = list(user.pet_set.all())
    if pets:
        if user.displayed_pet in pets:
            current_index = pets.index(user.displayed_pet)
        else:
            current_index = 0
        next_index = (current_index + 1) % len(pets)
        user.displayed_pet = pets[next_index]
        user.save()
    return redirect("home")


@login_required
def select_accessory(request):
    # Renders the accessory selection page for the user's displayed pet.
    user = request.user
    pet = user.displayed_pet
    user_hat_items = UserItem.objects.filter(user=user, shopitem__is_hat=True)

    if request.method == 'POST':
        selected_item_id = request.POST.get('selected_item_id')
        if selected_item_id:
            try:
                shop_item = ShopItem.objects.get(id=selected_item_id, is_hat=True)
                pet.hat = shop_item
                pet.save()
            except ShopItem.DoesNotExist:
                pass
        return redirect('home')
    
    context = {
        'pet': pet,
        'hat_items': user_hat_items,
        'points': user.points,
    }
    return render(request, 'select_accessory.html', context)


@login_required
def validate_qr(request, token):
    # Validates a QR code for an event.
    event = get_object_or_404(Event, unique_token=token)
    user_event = get_object_or_404(UserEvent, event=event, user=request.user)
    if not user_event.validated:
        user_event.validated = True
        user_event.save()
    return redirect("events")


@login_required
def leaderboard_view(request):
    # Generate a leaderboard based on users' highest pet level, without slicing
    top_users = list(
        CustomUser.objects.annotate(highest_pet_level_db=Max('pet__pet_level'))
        .filter(highest_pet_level_db__isnull=False)
        .order_by('-highest_pet_level_db')
    )
    
    # Replace each user's displayed_pet with the pet that has the highest level.
    for user in top_users:
        highest_pet = user.pet_set.order_by('-pet_level').first()
        user.displayed_pet = highest_pet

    context = {}
    if len(top_users) > 0:
        context['top_pet'] = top_users[0]  # 1st place
    if len(top_users) > 1:
        context['second_pet'] = top_users[1]  # 2nd place
    if len(top_users) > 2:
        context['third_pet'] = top_users[2]  # 3rd place
    context['leaderboard_entries'] = top_users[3:] if len(top_users) > 3 else []
    context['points'] = request.user.points
    return render(request, "leaderboard.html", context)



@login_required
def qr_scanner_view(request):
    # Renders the QR scanner page.
    return render(request, "qr_scanner.html")


@gamekeeper_required
@login_required
def gamekeeper_task_view(request):
    # Displays tasks created by the gamekeeper (predefined tasks).
    tasks = Task.objects.filter(creator=request.user, predefined=True)
    context = {
        "tasks": tasks,
        "points": request.user.points,
    }
    return render(request, "gamekeeper_tasks.html", context)


@gamekeeper_required
@login_required
def add_gamekeeper_task(request):
    """
    Allows gamekeepers to create new tasks.
    Expects JSON data with task details.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            task_name = data.get("task_name")
            description = data.get("description")
            points_given = data.get("points_given", 20)
            xp_given = data.get("xp_given", 20)
            predefined = True

            new_task = Task.objects.create(
                task_name=task_name,
                description=description,
                points_given=points_given,
                xp_given=xp_given,
                predefined=predefined,
                creator=request.user
            )

            return JsonResponse({
                "success": True,
                "message": "Task created successfully.",
                "task_id": new_task.task_id,
                "task_name": new_task.task_name,
                "description": new_task.description
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data."}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)


@gamekeeper_required
@login_required
def delete_gamekeeper_task(request, task_id):
    # Allows gamekeepers to delete their own predefined tasks.
    if request.method == "POST":
        task = get_object_or_404(Task, task_id=task_id, creator=request.user, predefined=True)
        task.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)
