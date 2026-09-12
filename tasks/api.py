from typing import Optional

from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema

from .models import Task

api = NinjaAPI(title="TaskHub API")


class TaskIn(Schema):
    title: str
    description: str = ""
    completed: bool = False


class TaskPatch(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskOut(Schema):
    id: int
    title: str
    description: str
    completed: bool
    attachment_path: str
    attachment_name: str
    created_at: str
    updated_at: str


def task_data(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "attachment_path": task.attachment_path,
        "attachment_name": task.attachment_name,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


@api.get("/tasks", response=list[TaskOut])
def list_tasks(request):
    return [task_data(task) for task in Task.objects.all()]


@api.get("/tasks/{task_id}", response=TaskOut)
def get_task(request, task_id: int):
    return task_data(get_object_or_404(Task, pk=task_id))


@api.post("/tasks", response={201: TaskOut})
def create_task(request, payload: TaskIn):
    return 201, task_data(Task.objects.create(**payload.model_dump()))


@api.patch("/tasks/{task_id}", response=TaskOut)
def update_task(request, task_id: int, payload: TaskPatch):
    task = get_object_or_404(Task, pk=task_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    task.save()
    return task_data(task)


@api.delete("/tasks/{task_id}")
def delete_task(request, task_id: int):
    task = get_object_or_404(Task, pk=task_id)
    task.delete()
    return {"success": True}
