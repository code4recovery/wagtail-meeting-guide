# Generated by Django 2.2.5 on 2020-03-22 00:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meeting_guide', '0007_auto_20200317_1933'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meeting',
            old_name='payment_paypal',
            new_name='paypal',
        ),
        migrations.RenameField(
            model_name='meeting',
            old_name='payment_venmo',
            new_name='venmo',
        ),
        migrations.RenameField(
            model_name='meeting',
            old_name='video_conference_dial_in',
            new_name='video_conference_phone',
        ),
    ]
