from .models import Alert

def create_alert(
    branch,
    camera,
    alert_type,
    severity,
    message
):
    Alert.objects.create(
        branch=branch,
        camera=camera,
        alert_type=alert_type,
        severity=severity,
        message=message
    )