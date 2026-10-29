from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("branches", "0001_initial")]
    operations = [
        migrations.AddField(model_name="camera", name="stream_status", field=models.CharField(choices=[("stopped", "Stopped"), ("running", "Running"), ("stopping", "Stopping"), ("error", "Error")], default="stopped", max_length=20)),
        migrations.AddField(model_name="camera", name="occupancy", field=models.IntegerField(blank=True, null=True)),
        migrations.AddField(model_name="camera", name="queue_length", field=models.IntegerField(blank=True, null=True)),
        migrations.AddField(model_name="camera", name="estimated_wait_time", field=models.IntegerField(blank=True, null=True)),
        migrations.AddField(model_name="camera", name="last_seen", field=models.DateTimeField(blank=True, null=True)),
    ]
