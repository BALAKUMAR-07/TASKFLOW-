"""
Forms for the TaskFlow tasks application.

Django forms handle:
  1. Rendering HTML form fields
  2. Validating submitted data
  3. Converting data to Python objects (cleaning)

We use ModelForm because our form maps directly to the Task model.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Task


class TaskForm(forms.ModelForm):
    """
    Form for creating and editing tasks.

    ModelForm automatically generates fields from the Task model.
    We customize widgets and add extra validation.
    """

    class Meta:
        model = Task
        # 'user' is excluded — we set it automatically in the view
        # from request.user so users cannot forge ownership.
        fields = ['title', 'description', 'status', 'priority', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title...',
                'autofocus': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the task (optional)...',
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',   # Renders as an HTML5 date picker
            }),
        }
        labels = {
            'due_date': 'Due Date (optional)',
            'description': 'Description (optional)',
        }

    def clean_due_date(self):
        """
        Custom validation: prevent setting due dates in the past.

        Django calls clean_<fieldname>() automatically during validation.
        Raise forms.ValidationError to reject the value.
        """
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now().date():
            raise forms.ValidationError(
                'Due date cannot be in the past. Please choose a future date.'
            )
        return due_date

    def clean_title(self):
        """Strip extra whitespace from the title."""
        title = self.cleaned_data.get('title', '')
        return title.strip()


class CustomUserCreationForm(UserCreationForm):
    """
    Extended registration form that adds an email field.

    UserCreationForm provides username, password1, password2.
    We add email and apply Bootstrap CSS classes to all fields.
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com',
        }),
        help_text='Enter a valid email address.',
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to inherited fields
        for field_name in ['username', 'password1', 'password2']:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        """Ensure the email address is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'This email address is already registered.'
            )
        return email

    def save(self, commit=True):
        """Save the user with the email field."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
