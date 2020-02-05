# Generated by Django 2.2.7 on 2020-01-10 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting_guide', '0003_location_postal_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meeting',
            old_name='meeting_details',
            new_name='details',
        ),
        migrations.RemoveField(
            model_name='group',
            name='area',
        ),
        migrations.RemoveField(
            model_name='group',
            name='district',
        ),
        migrations.RemoveField(
            model_name='meeting',
            name='location_details',
        ),
        migrations.AddField(
            model_name='location',
            name='details',
            field=models.TextField(blank=True, help_text="Details specific to the location, not the meeting. For example, 'Located in shopping center behind the bank.'", null=True),
        ),
        migrations.AddField(
            model_name='meeting',
            name='area',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='meeting',
            name='district',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]