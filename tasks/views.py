from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TaskForm
from .models import Task
from .storage import attachment_url, upload_attachment


def home(request):
    return render(request, "home.html")


def task_queryset(request):
    status = request.GET.get("status", "all")
    search = request.GET.get("q", "").strip()
    tasks = Task.objects.all()
    if status == "open":
        tasks = tasks.filter(completed=False)
    elif status == "completed":
        tasks = tasks.filter(completed=True)
    if search:
        tasks = tasks.filter(Q(title__icontains=search) | Q(description__icontains=search))
    return tasks


def task_list(request):
    return render(request, "tasks/task_list.html", {"tasks": task_queryset(request), "form": TaskForm()})


def task_list_partial(request):
    # HTMX sends GET with status/q; this view returns only task cards. hx-target points
    # at #task-list, and hx-swap="innerHTML" replaces its contents without a reload.
    return render(request, "tasks/_task_list.html", {"tasks": task_queryset(request)})


def task_create(request):
    form = TaskForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        uploaded_file = form.cleaned_data.get("attachment")
        if uploaded_file:
            task.attachment_path, task.attachment_name = upload_attachment(uploaded_file)
        task.save()
        if request.headers.get("HX-Request"):
            # HTMX sends POST form data here; return one rendered card. hx-target="#task-list"
            # chooses the list, and hx-swap="afterbegin" inserts the card at its beginning.
            return render(request, "tasks/_task_card.html", {"task": task})
        return redirect("tasks:list")
    return render(request, "tasks/task_form.html", {"form": form})


def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(request.POST or None, request.FILES or None, instance=task)
    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        uploaded_file = form.cleaned_data.get("attachment")
        if uploaded_file:
            task.attachment_path, task.attachment_name = upload_attachment(uploaded_file)
        task.save()
        return redirect("tasks:detail", pk=task.pk)
    return render(request, "tasks/task_detail.html", {"task": task, "form": form, "attachment_url": attachment_url(task.attachment_path)})


def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.completed = not task.completed
    task.save(update_fields=["completed", "updated_at"])
    # HTMX sends POST here; this returns the updated card. hx-target="closest article"
    # selects the current card, and hx-swap="outerHTML" replaces that whole card.
    return render(request, "tasks/_task_card.html", {"task": task})


def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    # HTMX sends DELETE here; an empty response plus hx-swap="outerHTML" removes the
    # card selected by hx-target="closest article" without JavaScript DOM code.
    return HttpResponse("")
