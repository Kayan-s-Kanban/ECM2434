from django.urls import path
from django.contrib import admin
from . import views
from django.contrib.auth.views import LogoutView
from .views import login_view, signup_view, delete_account, change_password, change_username, update_fontsize, get_fontsize, leaderboard_view, validate_qr


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.index, name="login"),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path("home/", views.home_view, name="home"),  
    path("settings/", views.settings_view, name="settings"),  
    path("tasks/", views.tasks_view, name="tasks"),
    path("tasks/add/", views.add_task, name="add_task"),
    path("tasks/complete/<int:task_id>/", views.complete_task, name="complete_task"),
    path('tasks/delete/<int:user_task_id>/', views.delete_task, name='delete_task'),
    path("events/", views.events_view, name="events"),
    path("events/joinevent/", views.join_event, name="join_event"),
    path("events/leaveevent/", views.leave_event, name="leave_event"),
    path("events/completeevent/", views.complete_event, name="complete_event"),
    path("events/createevent/", views.create_event, name="create_event"),
    path("events/gettasks/<int:event_id>/", views.get_event_tasks, name="get_event_tasks"),
    path('delete-account/', delete_account, name='delete_account'),
    path("change_password/", change_password, name="change_password"),
    path("change_username/", change_username, name="change_username"),
    path("update-fontsize/", update_fontsize, name="update_fontsize"),
    path("get-fontsize/", get_fontsize, name="get_fontsize"),
    path("term_of_use/",views.terms_view, name="term_of_use"),
    path('logout/', views.logout_view, name='logout'),
    path("shop/", views.shop_view, name="shop"),
    path("shop/buy/<int:item_id>/", views.buy_item, name="buy_item"),
    path('validate/<uuid:token>/', validate_qr, name='validate_qr'),
    path("leaderboard/", leaderboard_view, name="leaderboard"),
    path("qr_scanner/", views.qr_scanner_view, name="qr_scanner"),
    path("gamekeeper_tasks", views.gamekeeper_task_view, name="gamekeeper_tasks"),
    path("gamekeeper_tasks/add/", views.add_gamekeeper_task, name="add_gamekeeper_task"),
    path("gamekeeper_tasks/delete/<int:task_id>/", views.delete_gamekeeper_task, name="delete_gamekeeper_task"),
    path('cycle_pet/', views.cycle_pet, name='cycle_pet'),
]