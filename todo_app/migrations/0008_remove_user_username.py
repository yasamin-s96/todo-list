# Generated by Django 5.0 on 2023-12-26 13:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('todo_app', '0007_remove_user_full_name_alter_task_is_complete'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]
