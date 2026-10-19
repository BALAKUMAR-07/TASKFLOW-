"""
Views for the TaskFlow tasks application.

Views are Python functions that:
  1. Receive an HTTP request
  2. Process data (query database, validate forms)
  3. Return an HTTP response (rendered HTML or redirect)

Security principles applied here:
  - @login_required: redirects anonymous users to the login page
  - get_object_or_404: returns 404 (not 403) if a task doesn't exist
  - task.user == request.user: verifies the logged-in user owns the task
  - CSRF tokens: required by Django for all POST forms
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import HttpResponseForbidden

from .models import Task
from .forms import TaskForm, CustomUserCreationForm


# ---------------------------------------------------------------------------
# Index — redirect to dashboard or login
# ---------------------------------------------------------------------------

def index(request):
    """
    Root URL handler.
    Authenticated users go to the dashboard.
    Anonymous users go to the login page.
    """
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')
    return redirect('login')


# ---------------------------------------------------------------------------
# User Registration
# ---------------------------------------------------------------------------

def register(request):
    """
    Handles user registration.

    GET  -> Show the empty registration form.
    POST -> Validate and save the new user, then log them in.
    """
    # If the user is already logged in, send them to the dashboard
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the new user in immediately after registration
            login(request, user)
            messages.success(
                request,
                f'Welcome to TaskFlow, {user.username}! Your account has been created.'
            )
            return redirect('tasks:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@login_required
def dashboard(request):
    """
    Shows the user's task statistics and recent tasks.

    We use Django ORM aggregation to count tasks by status
    and calculate overdue tasks — all in a single database query
    where possible.

    @login_required: if not logged in, redirects to LOGIN_URL
    """
    today = timezone.now().date()
    user_tasks = Task.objects.filter(user=request.user)

    # Count tasks by status
    total_tasks    = user_tasks.count()
    todo_tasks     = user_tasks.filter(status=Task.Status.TODO).count()
    inprogress_tasks = user_tasks.filter(status=Task.Status.IN_PROGRESS).count()
    completed_tasks = user_tasks.filter(status=Task.Status.COMPLETED).count()

    # Overdue: due_date < today AND status != COMPLETED
    overdue_tasks = user_tasks.filter(
        due_date__lt=today,
        status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS]
    ).count()

    # Recent tasks for the dashboard preview (last 5)
    recent_tasks = user_tasks.select_related('user').order_by('-created_at')[:5]

    # High priority incomplete tasks
    high_priority_tasks = user_tasks.filter(
        priority=Task.Priority.HIGH
    ).exclude(status=Task.Status.COMPLETED).order_by('due_date')[:5]

    context = {
        'total_tasks':       total_tasks,
        'todo_tasks':        todo_tasks,
        'inprogress_tasks':  inprogress_tasks,
        'completed_tasks':   completed_tasks,
        'overdue_tasks':     overdue_tasks,
        'recent_tasks':      recent_tasks,
        'high_priority_tasks': high_priority_tasks,
        'pending_tasks':     todo_tasks + inprogress_tasks,
    }
    return render(request, 'tasks/dashboard.html', context)


# ---------------------------------------------------------------------------
# Task List with Search, Filter, Sort, Pagination
# ---------------------------------------------------------------------------

@login_required
def task_list(request):
    """
    Lists the logged-in user's tasks with optional search, filter, and sorting.

    URL parameters (all optional):
      ?search=keyword    — filter by title containing keyword
      ?status=TODO       — filter by status
      ?priority=HIGH     — filter by priority
      ?overdue=1         — show only overdue tasks
      ?sort=due_date     — sort field
      ?page=2            — pagination
    """
    today = timezone.now().date()
    tasks = Task.objects.filter(user=request.user)

    # --- Search ---
    search_query = request.GET.get('search', '').strip()
    if search_query:
        # Q objects allow OR-ing multiple conditions
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # --- Filter by status ---
    status_filter = request.GET.get('status', '')
    if status_filter and status_filter in dict(Task.Status.choices):
        tasks = tasks.filter(status=status_filter)

    # --- Filter by priority ---
    priority_filter = request.GET.get('priority', '')
    if priority_filter and priority_filter in dict(Task.Priority.choices):
        tasks = tasks.filter(priority=priority_filter)

    # --- Overdue filter ---
    overdue_filter = request.GET.get('overdue', '')
    if overdue_filter == '1':
        tasks = tasks.filter(
            due_date__lt=today,
            status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS]
        )

    # --- Sorting ---
    VALID_SORT_FIELDS = {
        'due_date':    'due_date',
        '-due_date':   '-due_date',
        'created_at':  'created_at',
        '-created_at': '-created_at',
        'priority':    'priority',
        'title':       'title',
    }
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by not in VALID_SORT_FIELDS:
        sort_by = '-created_at'
    tasks = tasks.order_by(VALID_SORT_FIELDS[sort_by])

    # --- Pagination (10 tasks per page) ---
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj':       page_obj,
        'search_query':   search_query,
        'status_filter':  status_filter,
        'priority_filter': priority_filter,
        'overdue_filter': overdue_filter,
        'sort_by':        sort_by,
        'status_choices': Task.Status.choices,
        'priority_choices': Task.Priority.choices,
        'today':          today,
        'total_count':    paginator.count,
    }
    return render(request, 'tasks/task_list.html', context)


# ---------------------------------------------------------------------------
# Task Detail
# ---------------------------------------------------------------------------

@login_required
def task_detail(request, pk):
    """
    Shows the details of a single task.

    get_object_or_404: if the task ID doesn't exist, return a 404 page.
    We then check ownership — if the task belongs to someone else,
    return 403 Forbidden.
    """
    task = get_object_or_404(Task, pk=pk)

    # Ownership check — never show another user's task
    if task.user != request.user:
        return HttpResponseForbidden(
            'You do not have permission to view this task.'
        )

    return render(request, 'tasks/task_detail.html', {'task': task})


# ---------------------------------------------------------------------------
# Task Create
# ---------------------------------------------------------------------------

@login_required
def task_create(request):
    """
    Handles task creation.

    GET  -> Show an empty TaskForm.
    POST -> Validate the form and save the new task.

    Important: we set task.user = request.user before saving.
    This prevents users from assigning tasks to other users.
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)  # Don't save to DB yet
            task.user = request.user         # Assign ownership
            task.save()                      # Now save to DB
            messages.success(
                request,
                f'Task "{task.title}" created successfully!'
            )
            return redirect('tasks:task_detail', pk=task.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm()

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'form_title': 'Create New Task',
        'submit_label': 'Create Task',
    })


# ---------------------------------------------------------------------------
# Task Edit
# ---------------------------------------------------------------------------

@login_required
def task_edit(request, pk):
    """
    Handles task editing.

    GET  -> Show the TaskForm pre-filled with current task data.
    POST -> Validate and save changes.
    """
    task = get_object_or_404(Task, pk=pk)

    if task.user != request.user:
        return HttpResponseForbidden(
            'You do not have permission to edit this task.'
        )

    if request.method == 'POST':
        # instance=task tells the form to UPDATE this task, not create a new one
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Task "{task.title}" updated successfully!'
            )
            return redirect('tasks:task_detail', pk=task.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'task': task,
        'form_title': f'Edit Task: {task.title}',
        'submit_label': 'Save Changes',
    })


# ---------------------------------------------------------------------------
# Task Delete
# ---------------------------------------------------------------------------

@login_required
def task_delete(request, pk):
    """
    Handles task deletion with a confirmation step.

    GET  -> Show a confirmation page asking the user to confirm deletion.
    POST -> Delete the task and redirect to the task list.

    We NEVER delete on GET — that would allow deletion via a shared link.
    """
    task = get_object_or_404(Task, pk=pk)

    if task.user != request.user:
        return HttpResponseForbidden(
            'You do not have permission to delete this task.'
        )

    if request.method == 'POST':
        title = task.title  # Save title before deletion for the message
        task.delete()
        messages.success(request, f'Task "{title}" has been deleted.')
        return redirect('tasks:task_list')

    # GET: Show the confirmation page
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})
