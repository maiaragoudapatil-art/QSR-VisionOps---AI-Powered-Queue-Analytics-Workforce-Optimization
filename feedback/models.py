from django.db import models
from branches.models import Branch
from staff.models import Staff


class Feedback(models.Model):

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE
    )

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    comments = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.staff.name} - {self.rating}"


class CustomerFeedback(models.Model):
    customer = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="customer_feedback",
    )
    staff = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_feedback",
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_feedback",
    )
    rating = models.PositiveSmallIntegerField()
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} - {self.rating}"