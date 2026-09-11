from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_rename_tasks_project_status_idx_tasks_project_fe19a5_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='airtable_record_id',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
