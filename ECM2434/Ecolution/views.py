import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, Http404
from django.db import IntegrityError
from .models import Task, UserTask, CustomUser, Pet, Event, UserEvent  

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the Ecolution index")

User = get_user_model()

def signup_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        pet_type = request.POST.get("pet_type", "mushroom")  # Default to mushroom
        plant_name = request.POST.get("plant_name", "") if pet_type == "plant" else None

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return render(request, "signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, "signup.html")

        # Create and save the new user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        # Assign a pet to the new user
        pet = Pet.objects.create(user=user, pet_name=plant_name if plant_name else pet_type, pet_type=pet_type)
        pet.save()

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

@login_required
def home_view(request):
    user = request.user  # Get the logged-in user
    pet = Pet.objects.filter(user=user).first()  

    context = {
        "points": user.points,
        "pet_exp": pet.pet_exp if pet else 0,
        "pet_name": pet.pet_name if pet else "No Pet",
        "pet_type": pet.pet_type.lower() if pet else "default",
        "pet_size": pet.determine_size() if pet else "small",  # Determine size
        "level": pet.pet_level if pet else 0,
        "pet": pet,
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
        "custom_tasks": custom_tasks
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
    """Marks a UserTask as completed."""
    if request.method == "POST":
        user_task = get_object_or_404(UserTask, task__task_id=task_id, user=request.user)
        user_task.completed = True
        user_task.save()
        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error"}, status=400)

def events_view(request):
    all_user_events = UserEvent.objects.filter(user=request.user)
    incomplete_user_events = UserEvent.objects.filter(user=request.user, completed = False)
    all_events = Event.objects.exclude(event_id__in=all_user_events.values_list("event_id", flat=True))
    context = {"user_events": incomplete_user_events, "events": all_events}
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

def complete_event(request):
    if request.method == "POST":
        try:
            event_id = request.POST.get("event_id")
            event = get_object_or_404(Event, event_id=event_id)
            event_points = event.total_points
            UserEvent.objects.filter(user=request.user, event=event).update(completed=True)
            CustomUser.objects.filter(id=request.user.id).update(points=request.user.points + event_points)

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request"})

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
    return render(request, "settings.html")

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


@csrf_exempt
@login_required
def update_fontsize(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_font_size = int(data.get("preferred_font_size", 3))
            request.user.preferred_font_size = new_font_size
            request.user.save()
            print(f"Updated font size to: {request.user.preferred_font_size}")  # Debugging
            return JsonResponse({"status": "success", "preferred_font_size": request.user.preferred_font_size})
        except Exception as e:
            print(f"Error updating font size: {e}")  # Debugging
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid request"})

@login_required
def get_fontsize(request):
    return JsonResponse({"preferred_font_size": request.user.preferred_font_size})    