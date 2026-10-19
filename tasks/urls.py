"""
URL patterns for the tasks application.

Each path() maps a URL to a view function.
We follow RESTful conventions where possible:

  /                     -> redirect to dashboard
  /dashboard/           -> dashboard with statistics
  /register/            -> user registration
  /tasks/               -> task list with search/filter
  /tasks/create/        -> create a new task
  /tasks/<id>/          -> task detail
  /tasks/<id>/edit/     -> edit a task
  /tasks/<id>/delete/   -> delete confirmation
"""

from django.urls import path
from . import views

app_name = 'tasks'  # Namespace — use 'tasks:dashboard' in templates

urlpatterns = [
    # Root URL redirects to dashboard
    path('', views.index, name='index'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Authentication
    path('register/', views.register, name='register'),

    # Task CRUD
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
]
