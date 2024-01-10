from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from .managers import TaskManager
from .managers import CustomUserManager


# Create your models here.
class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    age = models.IntegerField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Task(models.Model):
    content = models.CharField(max_length=150, verbose_name="Task")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    category = models.ForeignKey("Category", null=True, on_delete=models.SET_NULL, related_name="tasks")
    is_complete = models.BooleanField(default=False)
    task_due = models.DateTimeField(default=timezone.now, verbose_name="Task due time")
    task_modified = models.DateTimeField(auto_now=True)

    objects = TaskManager()

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        return reverse("todo_app:task_detail", kwargs={"task_id": self.id})

    class Meta:
        ordering = ["task_due"]


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    content = models.CharField(max_length=150, verbose_name="Category")
    slug = models.SlugField(max_length=20, blank=True)

    def save(
            self, *args, **kwargs
    ):
        self.content = self.content.title()
        if not self.slug:
            self.slug = slugify(self.content)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ['user', 'slug']
