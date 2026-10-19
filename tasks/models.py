"""
Task model for TaskFlow.

This module defines the database structure for tasks.
Each field maps directly to a column in the MySQL table.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    """
    Represents a single task owned by a user.

    Relationships:
        user -> Django's built-in User model (many tasks per user)

    The Meta class adds database indexes for fields we commonly
    filter or sort by, which makes queries faster.
    """

    # -----------------------------------------------------------------------
    # Status choices — stored as short strings in the database
    # -----------------------------------------------------------------------
    class Status(models.TextChoices):
        TODO        = 'TODO',        'To Do'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED   = 'COMPLETED',   'Completed'

    # -----------------------------------------------------------------------
    # Priority choices
    # -----------------------------------------------------------------------
    class Priority(models.TextChoices):
        LOW    = 'LOW',    'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH   = 'HIGH',   'High'

    # -----------------------------------------------------------------------
    # Fields
    # -----------------------------------------------------------------------

    # ForeignKey links each task to exactly one user.
    # on_delete=CASCADE means: if the user is deleted, all their tasks
    # are also deleted.
    # related_name='tasks' lets us write user.tasks.all() to get all tasks
    # belonging to a user.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Owner',
    )

    title = models.CharField(
        max_length=150,
        verbose_name='Title',
        help_text='A short, descriptive title for the task (max 150 characters).',
    )

    description = models.TextField(
        blank=True,       # Allows empty string in forms
        null=True,        # Stores NULL in the database when empty
        verbose_name='Description',
        help_text='Optional detailed description of the task.',
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        verbose_name='Status',
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name='Priority',
    )

    due_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Due Date',
        help_text='Optional deadline for the task.',
    )

    # auto_now_add=True: Django automatically sets this to 'now' when the
    # record is first created. It cannot be changed afterward.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At',
    )

    # auto_now=True: Django automatically updates this every time the
    # record is saved.
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At',
    )

    # -----------------------------------------------------------------------
    # Meta options
    # -----------------------------------------------------------------------
    class Meta:
        # Default ordering: newest tasks first
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        # Database indexes speed up common queries
        indexes = [
            models.Index(fields=['user', 'status'],   name='idx_user_status'),
            models.Index(fields=['user', 'priority'], name='idx_user_priority'),
            models.Index(fields=['user', 'due_date'], name='idx_user_due_date'),
            models.Index(fields=['due_date'],          name='idx_due_date'),
        ]

    # -----------------------------------------------------------------------
    # Helper methods
    # -----------------------------------------------------------------------

    def __str__(self):
        """Human-readable representation used in admin and debug output."""
        return f'{self.title} ({self.get_status_display()})'

    def is_overdue(self):
        """
        Returns True if this task has a due date in the past and is
        not yet completed.

        Definition: overdue = due_date < today AND status != COMPLETED
        Tasks without a due date are never overdue.
        """
        if self.due_date and self.status != self.Status.COMPLETED:
            return self.due_date < timezone.now().date()
        return False

    def get_priority_badge_class(self):
        """Returns a Bootstrap CSS class for the priority badge."""
        return {
            'LOW':    'badge-low',
            'MEDIUM': 'badge-medium',
            'HIGH':   'badge-high',
        }.get(self.priority, 'badge-secondary')

    def get_status_badge_class(self):
        """Returns a CSS class name for the status badge."""
        return {
            'TODO':        'badge-todo',
            'IN_PROGRESS': 'badge-in-progress',
            'COMPLETED':   'badge-completed',
        }.get(self.status, 'badge-secondary')
