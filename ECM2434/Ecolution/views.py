import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, Http404
from django.db import IntegrityError
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from .models import Task, UserTask, CustomUser, Pet, Event, UserEvent, ShopItem, UserItem
from django.db.models import Max

# Create your views here.
def index(request):
    return redirect("home")

User = get_user_model()

def signup_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        pet_type = request.POST.get("pet_type", "mushroom")  # Default to mushroom
        pet_name = request.POST.get("pet_name", "") if pet_type else None

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return render(request, "signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, "signup.html")

        # Create the new user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        # Assign a pet to the new user
        pet = Pet.objects.create(user=user, pet_name=pet_name if pet_name else pet_type, pet_type=pet_type)
        pet.save()

        ## Assigns the pet to the user and saves the user
        user.displayed_pet = pet
        user.save()

        try:
            shop_item = ShopItem.objects.get(name__iexact=pet_type)
            UserItem.objects.create(user=user, shopitem=shop_item)
        except ShopItem.DoesNotExist:
            pass

        messages.success(request, "Account created! You can now log in.")
        return redirect("login")

    return render(request, "signup.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")  # Redirects to home.html
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")

@never_cache
def logout_view(request):
    logout(request)
    return redirect("login")  # replace 'home' with your actual home page URL name

@login_required
def home_view(request):
    user = request.user  # Get the logged-in user
    pet = request.user.displayed_pet # Get the pet displayed by the user
    # This retrieves the 5 most recent tasks by date to display on home page 
    user_tasks = UserTask.objects.filter(user=user, completed=False).order_by('date')[:5]
    
    context = {
        "points": user.points,
        "pet_exp": pet.pet_exp if pet else 0,
        "pet_name": pet.pet_name if pet else "No Pet",
        "pet_type": pet.pet_type.lower() if pet else "default",
        "pet_size": pet.determine_size() if pet else "small",  # Determine size
        "level": pet.pet_level if pet else 0,
        "pet": pet,
        "user_tasks":user_tasks
    }

    return render(request, 'home.html', context)


@login_required
def tasks_view(request):
    """
    Gets all of the tasks for a specific user and renders the task page
    """
    user_tasks = UserTask.objects.filter(user=request.user)
    # Predefined tasks are those created by a superuser (or another designated admin)
    predefined_tasks = Task.objects.filter(creator__is_superuser=True)
    # Custom tasks are those created by the current user
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
    Handles adding tasks to the users active task list and creating custom tasks.
    """
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        task_name = request.POST.get("task_name")
        description = request.POST.get("description")

        if task_id:
            # User selected an existing task. Either predefined or custom
            task = get_user_or_superuser_task(task_id, request.user)
        else:
            # User is creating a brand-new custom task.
            if Task.objects.filter(creator=request.user, task_name=task_name).exists():
                return JsonResponse({
                    "status": "error",
                    "message": "You already created a custom task with that title."
                }, status=400)
            # Creates a new task object
            task = Task.objects.create(
                task_name=task_name,
                description=description,
                creator=request.user
            )

        try:
            # Try to create a UserTask object
            UserTask.objects.create(user=request.user, task=task)
        # This will throw an exception if the user task already exists with the same date
        except IntegrityError:
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
    Takes a task_id and returns a Task object that is either owned bt the user
    or by a superuser.
    """
    # Try to get a user-created task
    try:
        return Task.objects.get(task_id=task_id, creator=user)
    except Task.DoesNotExist:
        pass

    # If that fails, try to get a superuser-created task
    try:
        return Task.objects.get(task_id=task_id, creator__is_superuser=True)
    except Task.DoesNotExist:
        raise Http404("Task not found or not accessible.")


@login_required
def delete_task(request, user_task_id):
    """Deletes a UserTask"""
    if request.method == "POST":
        user_task = get_object_or_404(UserTask, pk=user_task_id, user=request.user)
        user_task.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({"status": "error"}, status=400)


@login_required
def complete_task(request, task_id):
    if request.method == "POST":
        user_task = get_object_or_404(UserTask, task__task_id=task_id, user=request.user)
        if not user_task.completed:
            user_task.completed = True
            user_task.save()

            # Add points to the users total points
            task = user_task.task
            request.user.points += task.points_given
            request.user.save()

            # Add task xp to the pet's overall xp, currently this will just get the first pet in the list
            pet = request.user.displayed_pet
            if pet:
                pet.pet_exp += task.xp_given
                if pet.pet_exp >= 100:
                    pet.pet_level += 1
                    pet.pet_exp -= 100
                pet.save()
                
        return JsonResponse({"status": "success", "points": request.user.points})
    return JsonResponse({"status": "error"}, status=400)

def events_view(request):
    all_user_events = UserEvent.objects.filter(user=request.user)
    incomplete_user_events = UserEvent.objects.filter(user=request.user, completed = False)

    user_events = Event.objects.filter(event_id__in=incomplete_user_events.values_list("event_id", flat=True))
    all_events = Event.objects.exclude(event_id__in=all_user_events.values_list("event_id", flat=True))
    
    context = {"user_events": user_events, "events": all_events, "points": request.user.points}
    return render(request, "events.html", context)

def join_event(request):
    if request.method == "POST":
        try:
            event_id = request.POST.get("event_id")
            event = get_object_or_404(Event, event_id=event_id)
            UserEvent.objects.create(user=request.user, event=event)

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request"})

def leave_event(request):
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
    if request.method == "POST":
        try:
            event_id = request.POST.get("event_id")
            event = get_object_or_404(Event, event_id=event_id)
            user_event = get_object_or_404(UserEvent, user=request.user, event=event)
            
            # Check if the event has been validated
            if not user_event.validated:
                return JsonResponse({"success": False, "message": "Event not validated."})
            
            # Award points and xp since the event is validated.
            event_points = event.total_points
            CustomUser.objects.filter(id=request.user.id).update(points=request.user.points + event_points)
            
            event_xp = event.total_xp
            pet = request.user.displayed_pet
            if pet:
                pet.pet_exp += event_xp
                if pet.pet_exp >= 100:
                    pet.pet_level += 1
                    pet.pet_exp -= 100
                pet.save()
            
            # Mark the event as completed for the user.
            user_event.completed = True
            user_event.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request"})

def create_event(request):
    if request.method == "POST":
        event_name = request.POST.get("event_name")
        description = request.POST.get("description")
        location = request.POST.get("location")
        date = request.POST.get("date")
        time = request.POST.get("time")

        try:
            event = Event.objects.create(
                event_name=event_name,
                description=description,
                location=location,
                date=date,
                time=time,
            )

        except IntegrityError as e:
            return JsonResponse({"status": "error", "message": "Database Integrity Error: " + str(e)}, status=400)
    
        return JsonResponse({"status": "success", "event_id": event.event_id})

    return JsonResponse({"status": "error"}, status=400)
    
def get_event_tasks(request, event_id):
    try:    
        event = get_object_or_404(Event, event_id=event_id)
        tasks =  Task.objects.filter(event=event)

        tasks_data = [
            {
                "task_id": task.task_id,
                "task_name": task.task_name,
                "description": task.description,  # Add more fields as needed
                "points_given": task.points_given,
                "xp_given": task.xp_given,
            }
            for task in tasks
        ]

        return JsonResponse({"tasks": tasks_data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




def settings_view(request):
    user = request.user
    context = {
        "name" : user.username,
        "points": user.points
    }
    return render(request, "settings.html", context)

@login_required
def delete_account(request):
    user = request.user  # Get the logged-in user

    if request.method == "POST":
        # Delete all related data
        UserTask.objects.filter(user=user).delete()
        UserEvent.objects.filter(user=user).delete()
        Pet.objects.filter(user=user).delete()

        # Delete user account
        user.delete()

        # Log the user out
        logout(request)

        # Show a success message
        messages.success(request, "Your account has been deleted successfully.")
        
        # Redirect to the homepage or login page
        return redirect("home")  # Change "home" to your homepage URL name

    return render(request, "delete_account.html")


@login_required
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password1 = request.POST["new_password1"]
        new_password2 = request.POST["new_password2"]
        
        if new_password1 != new_password2:
            messages.error(request, "New passwords do not match!")
            return redirect("settings")

        user = request.user
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect!")
            return redirect("settings")

        user.set_password(new_password1)
        user.save()

        # Keep the user logged in after password change
        update_session_auth_hash(request, user)

        messages.success(request, "Password updated successfully!")
        return redirect("settings")

    return redirect("settings")

@login_required
def change_username(request):
    if request.method == "POST":
        current_username = request.POST["current_username"]
        new_username1 = request.POST["new_username1"]
        new_username2 = request.POST["new_username2"]
        
        if new_username1 != new_username2:
            messages.error(request, "New usernames do not match!")
            return redirect("settings")

        user = request.user
        if not user.check_username(current_username):
            messages.error(request, "Current username is incorrect!")
            return redirect("settings")

        user.set_username(new_username1)
        user.save()

        # Keep the user logged in after username change
        update_session_auth_hash(request, user)

        messages.success(request, "username updated successfully!")
        return redirect("settings")

    return redirect("settings")

@login_required
def update_fontsize(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Convert the incoming font size value to an integer.
            try:
                font_size = int(data.get("preferred_font_size"))
            except (TypeError, ValueError):
                return JsonResponse({"status": "error", "message": "Invalid font size"})

            # Validate against the numeric choices
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
    return JsonResponse({"preferred_font_size": request.user.preferred_font_size})


def terms_view(request):
    return render(request, "term.html")

@login_required
def shop_view(request):
    shop_items = ShopItem.objects.all()
    purchased_item_ids = UserItem.objects.filter(user=request.user).values_list('shopitem__id', flat=True)
    return render(request, "shop.html", {
        "shop_items": shop_items,
        "purchased_item_ids": list(purchased_item_ids)
    })

@login_required
def buy_item(request, item_id):
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
        
        request.user.points -= shop_item.price
        request.user.save()
        UserItem.objects.create(user=request.user, shopitem=shop_item)
        return JsonResponse({
            "status": "success",
            "message": "Purchase successful!",
            "item": shop_item.name,
            "remaining_points": request.user.points
        })
    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)

@login_required
def validate_qr(request, token):
    # Retrieve the event using the unique token
    event = get_object_or_404(Event, unique_token=token)
    
    # Retrieve the UserEvent linking the current user to the event
    user_event = get_object_or_404(UserEvent, event=event, user=request.user)
    
    # Mark the attendance as validated if not already done
    if not user_event.validated:
        user_event.validated = True
        user_event.save()
    
    # Return a JSON response with the validation message
    return redirect("events")

@login_required
def leaderboard_view(request):
    # Annotate each user with the maximum pet level among all their pets.
    top_users = list(
        CustomUser.objects.annotate(highest_pet_level_db=Max('pet__pet_level'))
        .filter(highest_pet_level_db__isnull=False)
        .order_by('-highest_pet_level_db')[:5]
    )
    
    # For each user, replace displayed_pet with the pet that has the highest level.
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
    # Remaining entries (positions 4 and 5)
    context['leaderboard_entries'] = top_users[3:] if len(top_users) > 3 else []
    
    # Include user's points if needed by base.html
    context['points'] = request.user.points
    return render(request, "leaderboard.html", context)

@login_required
def qr_scanner_view(request):
    return render(request, "qr_scanner.html")

