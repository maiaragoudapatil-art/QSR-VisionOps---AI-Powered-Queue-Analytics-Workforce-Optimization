from django.contrib import admin
from .models import LiveAnalytics, Alert

admin.site.register(LiveAnalytics)
admin.site.register(Alert)