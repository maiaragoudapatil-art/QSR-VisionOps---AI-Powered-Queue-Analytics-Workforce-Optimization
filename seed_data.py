import os
import django
import random

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core.settings"
)

django.setup()

from analytics.models import LiveAnalytics
from branches.models import Branch, Camera

branch = Branch.objects.first()
camera = Camera.objects.first()

for _ in range(20):
    LiveAnalytics.objects.create(
        branch=branch,
        camera=camera,
        customer_count=random.randint(10, 100),
        queue_length=random.randint(1, 20),
        average_wait_time=random.randint(10, 120),
        occupancy=random.randint(20, 95),
    )

print("data records inserted")