from django.urls import path
from django.contrib import admin
from . import views
from .views import login_view, signup_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.index, name="login"),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path("home/", views.home_view, name="home"),  
    path("tasks/", views.tasks_view, name="tasks"),
    path("tasks/add/", views.add_task, name="add_task"),
]