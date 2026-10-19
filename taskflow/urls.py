"""
TaskFlow URL configuration.

This is the main router. It delegates:
  - Admin URLs to Django's built-in admin site
  - Authentication URLs (login, logout) to Django's auth views
  - Everything else to the 'tasks' application
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin panel — only for superusers
    path('admin/', admin.site.urls),

    # Django's built-in auth views: login, logout, password change, etc.
    # These look for templates in registration/
    path('', include('django.contrib.auth.urls')),

    # Our tasks application handles all other routes
    path('', include('tasks.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
