import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("branches", "0001_initial"),
        ("feedback", "0002_customerfeedback"),
        ("staff", "0002_staff_created_at_staff_shift_alter_staff_employee_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerfeedback",
            name="staff",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="customer_feedback",
                to="staff.staff",
            ),
        ),
        migrations.AddField(
            model_name="customerfeedback",
            name="branch",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="customer_feedback",
                to="branches.branch",
            ),
        ),
    ]
