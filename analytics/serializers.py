from rest_framework import serializers
from .models import LiveAnalytics
from .models import Alert

class LiveAnalyticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = LiveAnalytics
        fields = "__all__"


class AlertSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alert
        fields = "__all__"
        
