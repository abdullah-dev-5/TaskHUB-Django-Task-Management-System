from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    attachment = forms.FileField(required=False)

    class Meta:
        model = Task
        fields = ["title", "description", "attachment"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Task title"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Optional details"}),
        }
