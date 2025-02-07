from django.urls import path
from . import views
from .views import login_view, signup_view


urlpatterns = [
    path("", views.index, name="index"),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
]