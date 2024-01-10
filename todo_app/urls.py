from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "todo_app"

urlpatterns = [
    path("", views.tasks_list, name="tasks_list"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("task/add/", views.add_tasks, name="add_task"),
    path("task/edit/<int:task_id>/", views.edit_task, name="edit_task"),
    path("category/add/", views.CreateCategoryView.as_view(), name="create_category"),
    path("category/<slug:category_slug>/", views.categorized_tasks, name="categorized"),
    path("history/", views.HistoryListView.as_view(), name="history"),
    path("upcoming/", views.UpcomingTaskListView.as_view(), name="upcoming_tasks"),
]
