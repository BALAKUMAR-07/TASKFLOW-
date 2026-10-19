"""
Tests for the TaskFlow tasks application.

We test:
  1. User registration and authentication
  2. Task CRUD operations
  3. Ownership and access control
  4. Form validation
  5. Search and filtering
  6. Dashboard statistics
  7. Overdue task logic
  8. Anonymous user redirects

Run with: python manage.py test tasks
"""

from datetime import date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from .models import Task
from .forms import TaskForm, CustomUserCreationForm


class UserAuthenticationTests(TestCase):
    """
    Tests for user registration, login, and logout.
    """

    def setUp(self):
        """Create a test user before each test."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            email='test@example.com',
        )

    def test_registration_page_loads(self):
        """The registration page should return 200 OK."""
        response = self.client.get(reverse('tasks:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')

    def test_user_can_register(self):
        """A new user can register and is redirected to the dashboard."""
        response = self.client.post(reverse('tasks:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPass456!',
            'password2': 'StrongPass456!',
        })
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_duplicate_email_rejected(self):
        """Registration fails if the email is already taken."""
        response = self.client.post(reverse('tasks:register'), {
            'username': 'anotheruser',
            'email': 'test@example.com',  # already used by setUp user
            'password1': 'StrongPass456!',
            'password2': 'StrongPass456!',
        })
        self.assertEqual(response.status_code, 200)  # stays on form
        self.assertContains(response, 'already registered')

    def test_user_can_login(self):
        """An existing user can log in."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPass123!',
        })
        self.assertEqual(response.status_code, 302)  # redirect to dashboard

    def test_user_can_logout(self):
        """A logged-in user can log out."""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_login_page_loads(self):
        """The login page should return 200 OK."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)


class AnonymousUserRedirectTests(TestCase):
    """
    Anonymous (not logged-in) users should be redirected to login
    when they try to access protected pages.
    """

    def setUp(self):
        self.client = Client()

    def test_dashboard_redirects_anonymous(self):
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_task_list_redirects_anonymous(self):
        response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(response.status_code, 302)

    def test_task_create_redirects_anonymous(self):
        response = self.client.get(reverse('tasks:task_create'))
        self.assertEqual(response.status_code, 302)


class TaskCRUDTests(TestCase):
    """
    Tests for creating, viewing, editing, and deleting tasks.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='taskuser', password='TestPass123!'
        )
        self.client.login(username='taskuser', password='TestPass123!')

        # Create a sample task
        self.task = Task.objects.create(
            user=self.user,
            title='Test Task',
            description='A test task description',
            status=Task.Status.TODO,
            priority=Task.Priority.MEDIUM,
        )

    def test_task_list_page_loads(self):
        response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')

    def test_task_detail_page_loads(self):
        response = self.client.get(
            reverse('tasks:task_detail', kwargs={'pk': self.task.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')

    def test_create_task(self):
        """POST to task_create with valid data creates a task."""
        future_date = (date.today() + timedelta(days=7)).isoformat()
        response = self.client.post(reverse('tasks:task_create'), {
            'title': 'New Task',
            'description': 'Created in test',
            'status': 'TODO',
            'priority': 'HIGH',
            'due_date': future_date,
        })
        self.assertEqual(response.status_code, 302)  # redirect after create
        self.assertTrue(Task.objects.filter(title='New Task').exists())

    def test_create_task_without_due_date(self):
        """Tasks can be created without a due date."""
        response = self.client.post(reverse('tasks:task_create'), {
            'title': 'No Due Date Task',
            'description': '',
            'status': 'TODO',
            'priority': 'LOW',
            'due_date': '',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='No Due Date Task').exists())

    def test_edit_task(self):
        """POST to task_edit with valid data updates the task."""
        future_date = (date.today() + timedelta(days=5)).isoformat()
        response = self.client.post(
            reverse('tasks:task_edit', kwargs={'pk': self.task.pk}),
            {
                'title': 'Updated Task',
                'description': 'Updated description',
                'status': 'IN_PROGRESS',
                'priority': 'HIGH',
                'due_date': future_date,
            }
        )
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
        self.assertEqual(self.task.status, 'IN_PROGRESS')

    def test_delete_task(self):
        """POST to task_delete removes the task from the database."""
        task_pk = self.task.pk
        response = self.client.post(
            reverse('tasks:task_delete', kwargs={'pk': task_pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=task_pk).exists())

    def test_delete_confirmation_page(self):
        """GET to task_delete shows a confirmation page (does not delete)."""
        response = self.client.get(
            reverse('tasks:task_delete', kwargs={'pk': self.task.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete')
        # Task should still exist
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())


class TaskOwnershipTests(TestCase):
    """
    Tests ensuring users can only access their own tasks.
    """

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1', password='TestPass123!'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='TestPass123!'
        )
        # Task belongs to user1
        self.task = Task.objects.create(
            user=self.user1,
            title='User1 Task',
            status=Task.Status.TODO,
            priority=Task.Priority.MEDIUM,
        )

    def test_user2_cannot_view_user1_task(self):
        """user2 gets a 403 when trying to view user1's task."""
        self.client.login(username='user2', password='TestPass123!')
        response = self.client.get(
            reverse('tasks:task_detail', kwargs={'pk': self.task.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_user2_cannot_edit_user1_task(self):
        self.client.login(username='user2', password='TestPass123!')
        response = self.client.post(
            reverse('tasks:task_edit', kwargs={'pk': self.task.pk}),
            {'title': 'Hacked', 'status': 'COMPLETED', 'priority': 'LOW'}
        )
        self.assertEqual(response.status_code, 403)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'User1 Task')  # unchanged

    def test_user2_cannot_delete_user1_task(self):
        self.client.login(username='user2', password='TestPass123!')
        response = self.client.post(
            reverse('tasks:task_delete', kwargs={'pk': self.task.pk})
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

    def test_task_list_only_shows_own_tasks(self):
        """user2's task list should not show user1's tasks."""
        Task.objects.create(
            user=self.user2,
            title='User2 Task',
            status=Task.Status.TODO,
            priority=Task.Priority.LOW,
        )
        self.client.login(username='user2', password='TestPass123!')
        response = self.client.get(reverse('tasks:task_list'))
        self.assertNotContains(response, 'User1 Task')
        self.assertContains(response, 'User2 Task')


class TaskFormValidationTests(TestCase):
    """
    Tests for form validation rules.
    """

    def test_task_form_valid_data(self):
        """Form is valid with correct data."""
        future_date = date.today() + timedelta(days=7)
        form = TaskForm(data={
            'title': 'Valid Task',
            'description': 'Some description',
            'status': 'TODO',
            'priority': 'MEDIUM',
            'due_date': future_date,
        })
        self.assertTrue(form.is_valid())

    def test_task_form_requires_title(self):
        """Form is invalid without a title."""
        form = TaskForm(data={
            'title': '',
            'status': 'TODO',
            'priority': 'MEDIUM',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_past_due_date_rejected(self):
        """Form is invalid when due date is in the past."""
        past_date = date.today() - timedelta(days=1)
        form = TaskForm(data={
            'title': 'Past Due Task',
            'status': 'TODO',
            'priority': 'MEDIUM',
            'due_date': past_date,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)

    def test_form_valid_without_due_date(self):
        """Due date is optional — form is valid without it."""
        form = TaskForm(data={
            'title': 'No Due Date',
            'status': 'TODO',
            'priority': 'LOW',
        })
        self.assertTrue(form.is_valid())


class SearchAndFilterTests(TestCase):
    """
    Tests for the search and filter functionality in the task list.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='filteruser', password='TestPass123!'
        )
        self.client.login(username='filteruser', password='TestPass123!')

        today = date.today()

        Task.objects.create(
            user=self.user, title='Alpha Task',
            status='TODO', priority='HIGH',
        )
        Task.objects.create(
            user=self.user, title='Beta Task',
            status='IN_PROGRESS', priority='MEDIUM',
        )
        Task.objects.create(
            user=self.user, title='Gamma Task',
            status='COMPLETED', priority='LOW',
        )
        # Overdue task
        Task.objects.create(
            user=self.user, title='Overdue Task',
            status='TODO', priority='HIGH',
            due_date=today - timedelta(days=3),
        )

    def test_search_by_title(self):
        response = self.client.get(reverse('tasks:task_list') + '?search=Alpha')
        self.assertContains(response, 'Alpha Task')
        self.assertNotContains(response, 'Beta Task')

    def test_filter_by_status(self):
        response = self.client.get(reverse('tasks:task_list') + '?status=COMPLETED')
        self.assertContains(response, 'Gamma Task')
        self.assertNotContains(response, 'Alpha Task')

    def test_filter_by_priority(self):
        response = self.client.get(reverse('tasks:task_list') + '?priority=HIGH')
        self.assertContains(response, 'Alpha Task')
        self.assertNotContains(response, 'Gamma Task')

    def test_filter_overdue(self):
        response = self.client.get(reverse('tasks:task_list') + '?overdue=1')
        self.assertContains(response, 'Overdue Task')
        self.assertNotContains(response, 'Alpha Task')
        self.assertNotContains(response, 'Gamma Task')  # completed tasks not overdue


class DashboardStatisticsTests(TestCase):
    """
    Tests for dashboard statistics accuracy.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='dashuser', password='TestPass123!'
        )
        self.client.login(username='dashuser', password='TestPass123!')

        today = date.today()

        Task.objects.create(user=self.user, title='T1', status='TODO', priority='LOW')
        Task.objects.create(user=self.user, title='T2', status='TODO', priority='LOW')
        Task.objects.create(user=self.user, title='T3', status='IN_PROGRESS', priority='MEDIUM')
        Task.objects.create(user=self.user, title='T4', status='COMPLETED', priority='HIGH')
        Task.objects.create(
            user=self.user, title='T5 Overdue',
            status='TODO', priority='HIGH',
            due_date=today - timedelta(days=2),
        )

    def test_dashboard_loads(self):
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_total_count(self):
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.context['total_tasks'], 5)

    def test_dashboard_completed_count(self):
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.context['completed_tasks'], 1)

    def test_dashboard_overdue_count(self):
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.context['overdue_tasks'], 1)

    def test_dashboard_inprogress_count(self):
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.context['inprogress_tasks'], 1)


class OverdueTaskTests(TestCase):
    """
    Tests for the is_overdue() model method.
    Definition: due_date < today AND status != COMPLETED.
    Tasks without due dates are never overdue.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='overdueuser', password='TestPass123!'
        )
        self.today = date.today()

    def _make_task(self, **kwargs):
        defaults = {
            'user': self.user,
            'title': 'Test',
            'status': Task.Status.TODO,
            'priority': Task.Priority.MEDIUM,
        }
        defaults.update(kwargs)
        return Task(**defaults)

    def test_past_due_todo_is_overdue(self):
        task = self._make_task(due_date=self.today - timedelta(days=1))
        self.assertTrue(task.is_overdue())

    def test_past_due_in_progress_is_overdue(self):
        task = self._make_task(
            due_date=self.today - timedelta(days=1),
            status=Task.Status.IN_PROGRESS,
        )
        self.assertTrue(task.is_overdue())

    def test_past_due_completed_is_not_overdue(self):
        task = self._make_task(
            due_date=self.today - timedelta(days=1),
            status=Task.Status.COMPLETED,
        )
        self.assertFalse(task.is_overdue())

    def test_future_due_is_not_overdue(self):
        task = self._make_task(due_date=self.today + timedelta(days=1))
        self.assertFalse(task.is_overdue())

    def test_no_due_date_is_not_overdue(self):
        task = self._make_task(due_date=None)
        self.assertFalse(task.is_overdue())

    def test_due_today_is_not_overdue(self):
        """A task due today is not yet overdue."""
        task = self._make_task(due_date=self.today)
        self.assertFalse(task.is_overdue())
