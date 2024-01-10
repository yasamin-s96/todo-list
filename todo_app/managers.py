from django.contrib.auth.models import BaseUserManager
from django.db.models import Manager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class TaskManager(Manager):
    def completed(self, user):
        return self.get_queryset().filter(user=user, is_complete=True)

    def due_passed(self, user):
        return self.get_queryset().filter(user=user, is_complete=False,
                                          task_due__date__lt=timezone.now().date()).order_by("task_due")

    def upcoming(self, user):
        return self.get_queryset().filter(user=user, is_complete=False, task_due__date__gt=timezone.now().date())

    def categorized(self, user, category):
        return self.get_queryset().filter(user=user, is_complete=False, category=category)

    def today_pending(self, user):
        return self.get_queryset().filter(user=user, is_complete=False, task_due__date=timezone.now().date())
