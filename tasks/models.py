from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Task(models.Model):
    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
    ]

    CATEGORY_CHOICES = [
        ("Work", "Work"),
        ("Personal", "Personal"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="Low")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="Work")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
