# Generated by Django 5.2.3 on 2025-07-01 15:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='verification',
            old_name='recovery_mail',
            new_name='email',
        ),
        migrations.RenameField(
            model_name='verification',
            old_name='expire',
            new_name='is_expired',
        ),
        migrations.RemoveField(
            model_name='verification',
            name='generate_time',
        ),
        migrations.RemoveField(
            model_name='verification',
            name='username',
        ),
    ]
