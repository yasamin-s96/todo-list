from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView
from .models import Task, Category
from .utils import handle_task_completion
from .forms import TaskForm, LoginForm, RegistrationForm, CreateCategoryForm


# Create your views here.
class CustomLoginView(LoginView):
    form_class = LoginForm


@login_required
def tasks_list(request):
    user = request.user
    # get the incomplete tasks till today.
    due_passed = Task.objects.due_passed(user=user)

    # get the tasks that belong to today's list.
    today_pending = Task.objects.today_pending(user=user)

    if request.method == "POST":
        # get all the values of checkboxes that are checked and named 'task'.
        # the value of the checkboxes are the task ids.
        task_ids = request.POST.getlist("task")
        delayed_tasks = due_passed.filter(id__in=task_ids)
        today_tasks = today_pending.filter(id__in=task_ids)

        if not task_ids:
            messages.error(request, "No task was checked")

        for task_list in (delayed_tasks, today_tasks):
            if task_list.exists():
                handle_task_completion(request, task_list)
                break

    return render(request, "todo_app/index.html",
                  {"today_tasks": today_pending, "incomplete_tasks": due_passed})


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            # create default categories for every newly-registered user
            Category.objects.bulk_create([
                Category(content="Personal", user=user, slug="personal"),
                Category(content="Free time", user=user, slug="free-time"),
                Category(content="Project", user=user, slug="project"),
                Category(content="School", user=user, slug="school")
            ])

            return redirect(reverse("todo_app:login"))
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def add_tasks(request):
    user = request.user
    categories = user.categories.all()
    if request.method == "POST":
        form = TaskForm(categories, request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.category.user = user
            task.save()
            messages.success(request, "Added task to your list")

            # if there's a hidden input called next, fetch its value(url), else use the default
            redirect_url = request.POST.get("next", reverse("todo_app:tasks_list"))
            return redirect(redirect_url)
    else:

        # check if there's a "category" query param inside request.GET
        category_slug = request.GET.get("category")
        if category_slug:
            category = get_object_or_404(Category, user=user, slug=category_slug)
            # fill the category field with the queried category
            form = TaskForm(initial={"category": category}, user_categories=categories)
            form.fields.pop("is_complete")
        else:
            # passing the user's categories to form for having dynamic choices in select box
            form = TaskForm(user_categories=categories)
            form.fields.pop("is_complete")
    return render(request, "todo_app/add_task.html", {"form": form})


@login_required
def edit_task(request, task_id):
    user = request.user
    categories = user.categories.all()
    task = get_object_or_404(user.tasks, pk=task_id)
    if request.method == "POST":
        # if there's a hidden input called next, fetch its value(url), else use the default
        redirect_url = request.POST.get("next", reverse("todo_app:edit_task", kwargs={"task_id": task.id}))
        if "edit" in request.POST:
            form = TaskForm(categories, instance=task, data=request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Task updated successfully")
                return redirect(redirect_url)

            else:
                messages.error(request, "Error occurred trying to update your task")
        elif "delete" in request.POST:
            task.delete()
            messages.success(request, "Task deleted successfully")
            return redirect(redirect_url)

    else:
        form = TaskForm(categories, instance=task)
    return render(request, "todo_app/task.html", {"form": form, "task": task})


@login_required
def categorized_tasks(request, category_slug):
    user = request.user
    category = get_object_or_404(Category, user=user, slug=category_slug)
    relevant_tasks = Task.objects.categorized(user=user, category=category)
    if request.method == "POST":
        task_ids = request.POST.getlist("task")
        if not task_ids:
            messages.error(request, "No task was checked")

        handle_task_completion(request, relevant_tasks.filter(id__in=task_ids))

    return render(request, "todo_app/categorized_tasks.html",
                  {"relevant_tasks": relevant_tasks, "category": category})


class UpcomingTaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "todo_app/upcoming_tasks.html"
    context_object_name = "upcoming_tasks"

    def get_queryset(self):
        return Task.objects.upcoming(user=self.request.user)


class HistoryListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "todo_app/history.html"
    context_object_name = "completed_tasks"

    def get_queryset(self):
        return Task.objects.completed(user=self.request.user)


class CreateCategoryView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ["content"]
    template_name = "todo_app/add_category.html"
    success_url = reverse_lazy("todo_app:tasks_list")

    def form_valid(self, form):
        user = self.request.user
        category = form.save(commit=False)
        category.user = user

        # the only integrity error that might occur at this point is related to the category.content
        # therefore I try to catch it if it did
        try:
            return super().form_valid(form)
        except IntegrityError as e:
            form.add_error("content", "The category you create shouldn't already exist in your category list")
            return self.form_invalid(form)
