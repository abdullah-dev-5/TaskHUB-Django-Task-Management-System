from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.home, name="home"),
    path("app/", views.task_list, name="list"),
    path("tasks/partial/", views.task_list_partial, name="partial"),
    path("tasks/create/", views.task_create, name="create"),
    path("tasks/<int:pk>/", views.task_detail, name="detail"),
    path("tasks/<int:pk>/toggle/", views.task_toggle, name="toggle"),
    path("tasks/<int:pk>/delete/", views.task_delete, name="delete"),
]
