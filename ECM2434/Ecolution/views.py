from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import Task, UserTask

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

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return render(request, "signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, "signup.html")

        # Create and save the new user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

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

def home_view(request):
    return render(request, "home.html")

@login_required
def tasks_view(request):
    user_tasks = UserTask.objects.filter(user=request.user)
    predefined_tasks = Task.objects.all()

    return render(request, "tasks.html", {"user_tasks": user_tasks, "predefined_tasks": predefined_tasks})

@login_required
def add_task(request):
    """Handles adding a predefined or custom task"""
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        task_name = request.POST.get("task_name")
        description = request.POST.get("description")

        if task_id:
            # User selected a predefined task
            task = get_object_or_404(Task, task_id=task_id)
        else:
            # User is creating a custom task
            task = Task.objects.create(task_name=task_name, description=description)

        # Assign task to the logged-in user
        UserTask.objects.create(user=request.user, task=task)

        return JsonResponse({"status": "success", "task_name": task.task_name, "description": task.description})

    return JsonResponse({"status": "error"}, status=400)

@login_required
def delete_task(request, task_id):
    """Deletes a UserTask for the logged-in user."""
    if request.method == "POST":
        user_task = get_object_or_404(UserTask, task__task_id=task_id, user=request.user)
        user_task.delete()
        return JsonResponse({"status": "success"})

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
    return render(request, "events.html")
