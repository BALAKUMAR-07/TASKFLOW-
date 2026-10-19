"""
Django Admin configuration for the tasks application.

The admin site lets superusers manage all data through a web interface.
We customize the display to make it more useful.
"""

from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Customizes how Tasks appear in the Django admin interface.
    """

    # Columns shown in the task list view
    list_display = (
        'title', 'user', 'status', 'priority',
        'due_date', 'is_overdue', 'created_at',
    )

    # Sidebar filters on the right side of the list
    list_filter = ('status', 'priority', 'created_at', 'user')

    # Fields that can be searched using the search box
    search_fields = ('title', 'description', 'user__username')

    # Make these fields clickable links in the list
    list_display_links = ('title',)

    # Default sort order in the admin list
    ordering = ('-created_at',)

    # Read-only fields (cannot be edited through admin)
    readonly_fields = ('created_at', 'updated_at')

    # Layout of fields on the detail/edit page
    fieldsets = (
        ('Task Information', {
            'fields': ('user', 'title', 'description'),
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'due_date'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),  # Collapsed by default
        }),
    )

    # Allow changing status/priority directly in the list without opening the record
    list_editable = ('status', 'priority')
