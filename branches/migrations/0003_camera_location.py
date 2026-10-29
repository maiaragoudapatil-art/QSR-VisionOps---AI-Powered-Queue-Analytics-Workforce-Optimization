from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("branches", "0002_camera_stream_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="camera",
            name="location",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
