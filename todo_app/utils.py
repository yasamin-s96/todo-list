from django.contrib import messages
from django.utils import timezone


def handle_task_completion(request, tasks):
    """
    Update the tasks user clicked on its form button
    :param request:
    :param tasks:
    :return:
    """

    if "reschedule_tasks" in request.POST:
        tasks.update(task_due=timezone.now())
        messages.success(request, "Rescheduled task(s) for today")

    elif "complete_tasks" in request.POST:
        tasks.update(is_complete=True)
        messages.success(request, "Completed task(s)")
