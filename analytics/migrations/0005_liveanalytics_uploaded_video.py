from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("analytics", "0004_uploadedvideo"),
    ]

    operations = [
        migrations.AddField(
            model_name="liveanalytics",
            name="uploaded_video",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="analytics_result",
                to="analytics.uploadedvideo",
            ),
        ),
    ]
