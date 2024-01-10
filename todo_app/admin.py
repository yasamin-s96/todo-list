from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'content')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'task_due', 'is_complete')
