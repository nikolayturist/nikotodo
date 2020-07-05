from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Todo(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)

    importance = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    @property
    def is_past_due(self):
        if self.due_date is None:
            return False

        return timezone.now() > self.due_date
