import json

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from tasks.models import Task


class TaskViewsTests(TestCase):
    def test_homepage_introduces_taskhub_and_links_to_app(self):
        response = self.client.get(reverse("tasks:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "See how a simple task app comes together.")
        self.assertContains(response, reverse("tasks:list"))

    def test_task_creation(self):
        response = self.client.post(reverse("tasks:create"), {"title": "Learn HTMX", "description": "Try a partial"})
        self.assertRedirects(response, reverse("tasks:list"))
        self.assertTrue(Task.objects.filter(title="Learn HTMX").exists())

    def test_task_attachment_uses_local_storage_without_supabase(self):
        upload = SimpleUploadedFile("notes.txt", b"TaskHub upload test", content_type="text/plain")
        response = self.client.post(
            reverse("tasks:create"),
            {"title": "Upload locally", "attachment": upload},
        )
        task = Task.objects.get(title="Upload locally")
        self.assertRedirects(response, reverse("tasks:list"))
        self.assertEqual(task.attachment_name, "notes.txt")
        self.assertTrue(default_storage.exists(task.attachment_path))
        default_storage.delete(task.attachment_path)

    def test_task_completion(self):
        task = Task.objects.create(title="Finish test")
        response = self.client.post(reverse("tasks:toggle", args=[task.pk]), HTTP_HX_REQUEST="true")
        task.refresh_from_db()
        self.assertTrue(task.completed)
        self.assertContains(response, "Reopen")

    def test_task_deletion(self):
        task = Task.objects.create(title="Remove me")
        response = self.client.delete(reverse("tasks:delete", args=[task.pk]), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_task_filtering_and_search(self):
        Task.objects.create(title="Open Django task", completed=False)
        Task.objects.create(title="Finished CSS task", completed=True)
        response = self.client.get(reverse("tasks:partial"), {"status": "open", "q": "Django"}, HTTP_HX_REQUEST="true")
        self.assertContains(response, "Open Django task")
        self.assertNotContains(response, "Finished CSS task")

    def test_same_named_tasks_are_both_returned_in_stable_order(self):
        first = Task.objects.create(title="Same name")
        second = Task.objects.create(title="Same name")
        response = self.client.get(reverse("tasks:partial"))
        self.assertContains(response, 'id="task-%s"' % first.pk)
        self.assertContains(response, 'id="task-%s"' % second.pk)
        self.assertLess(response.content.find(('task-%s' % second.pk).encode()), response.content.find(('task-%s' % first.pk).encode()))


class TaskApiTests(TestCase):
    def test_api_task_listing(self):
        Task.objects.create(title="API task")
        response = self.client.get("/api/tasks")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["title"], "API task")

    def test_api_task_creation(self):
        response = self.client.post(
            "/api/tasks",
            data=json.dumps({"title": "Created through API", "description": "Ninja"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["title"], "Created through API")
        self.assertTrue(Task.objects.filter(title="Created through API").exists())
