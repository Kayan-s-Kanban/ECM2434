from django.urls import path
from . import views
from .views import login_view, signup_view, settings_view, home_view, index


urlpatterns = [
    path("", index, name="index"),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path("home/", home_view, name="home"),  
    path("settings/", settings_view, name="settings"),  
]