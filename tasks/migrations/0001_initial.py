# Generated migration for the Task model
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='A short, descriptive title for the task (max 150 characters).', max_length=150, verbose_name='Title')),
                ('description', models.TextField(blank=True, help_text='Optional detailed description of the task.', null=True, verbose_name='Description')),
                ('status', models.CharField(choices=[('TODO', 'To Do'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed')], default='TODO', max_length=20, verbose_name='Status')),
                ('priority', models.CharField(choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')], default='MEDIUM', max_length=10, verbose_name='Priority')),
                ('due_date', models.DateField(blank=True, help_text='Optional deadline for the task.', null=True, verbose_name='Due Date')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to=settings.AUTH_USER_MODEL, verbose_name='Owner')),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['user', 'status'], name='idx_user_status'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['user', 'priority'], name='idx_user_priority'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['user', 'due_date'], name='idx_user_due_date'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['due_date'], name='idx_due_date'),
        ),
    ]
