from django.db import models
from branches.models import Branch


class Staff(models.Model):

    employee_id = models.CharField(
        max_length=20,
        unique=True
    )

    name = models.CharField(
        max_length=100
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE
    )

    shift = models.CharField(
        max_length=50
    )

    active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name