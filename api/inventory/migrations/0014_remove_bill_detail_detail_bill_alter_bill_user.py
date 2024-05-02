# Generated by Django 5.0.3 on 2024-05-02 15:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0013_role_permissions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bill',
            name='detail',
        ),
        migrations.AddField(
            model_name='detail',
            name='bill',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='details', to='inventory.bill'),
        ),
        migrations.AlterField(
            model_name='bill',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='bills', to=settings.AUTH_USER_MODEL),
        ),
    ]