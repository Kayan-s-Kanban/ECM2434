from django.urls import path
from . import views
from .views import login_view, signup_view


urlpatterns = [
    path("", views.index, name="login"),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path("home/", views.home_view, name="home"),  
]