# Generated by Django 3.0.8 on 2020-07-22 20:34

import django.core.validators
from django.db import migrations, models
import meeting_guide.validators


class Migration(migrations.Migration):

    dependencies = [
        ('meeting_guide', '0012_auto_20200405_1015'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='meetingtype',
            name='meeting_gui_meeting_e22f98_idx',
        ),
        migrations.RenameField(
            model_name='meeting',
            old_name='video_conference_url',
            new_name='conference_url',
        ),
        migrations.RenameField(
            model_name='meetingtype',
            old_name='meeting_guide_code',
            new_name='spec_code',
        ),
        migrations.RenameField(
            model_name='meeting',
            old_name='video_conference_phone',
            new_name='conference_phone',
        ),
        migrations.AddField(
            model_name='meeting',
            name='cashapp',
            field=models.TextField(blank=True, default='', help_text='Example: $aa-mygroup', max_length=31, validators=[meeting_guide.validators.CashAppUsernameValidator()], verbose_name='CashApp Account'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='conference_phone',
            field=models.CharField(blank=True, default='', help_text=('Enter a valid conference phone number. The three groups of numbers in this example are a Zoom phone number, meeting code, and password: +19294362866,,2151234215#,,#,,12341234#',), max_length=255, validators=[meeting_guide.validators.ConferencePhoneValidator()]),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='paypal',
            field=models.TextField(blank=True, default='', help_text='Example: aamygroup', max_length=255, validators=[meeting_guide.validators.PayPalUsernameValidator(), django.core.validators.MinLengthValidator(8)], verbose_name='PayPal Username'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='venmo',
            field=models.TextField(blank=True, default='', help_text='Example: @aa-mygroup', max_length=31, validators=[meeting_guide.validators.VenmoUsernameValidator()], verbose_name='Venmo Account'),
        ),
        migrations.AddIndex(
            model_name='meetingtype',
            index=models.Index(fields=['spec_code'], name='meeting_gui_spec_co_dfdefe_idx'),
        ),
    ]