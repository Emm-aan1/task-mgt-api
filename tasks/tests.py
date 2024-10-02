from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "testuser", "password": "testpass"},
        )
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        self.task_url = reverse("task-list-create")

    def test_create_task(self):
        data = {
            "title": "Test Task",
            "description": "Test Description",
            "due_date": "2024-10-05",
            "category": "Personal",
        }
        response = self.client.post(self.task_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().title, "Test Task")

    def test_delete_task(self):
        task = Task.objects.create(
            user=self.user,
            title="Test Task",
            description="Test Description",
            due_date="2024-10-05",
        )
        task_url = reverse("task-detail", kwargs={"pk": task.id})
        response = self.client.delete(task_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.count(), 0)


class LogoutTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "testuser", "password": "testpass"},
        )
        self.token = response.data["access"]
        self.refresh_token = response.data["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

    def test_logout(self):
        response = self.client.post(reverse("user-logout"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Logout successful")
