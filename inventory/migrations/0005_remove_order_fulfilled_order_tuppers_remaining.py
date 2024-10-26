# Generated by Django 5.1 on 2024-10-18 13:00

from django.db import migrations, models

def copy_tuppers_requested_to_remaining(apps, schema_editor):
    Order = apps.get_model('inventory', 'Order')
    for order in Order.objects.all():
        order.tuppers_remaining = order.tuppers_requested
        order.save()


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0004_cut_color"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="fulfilled",
        ),
        migrations.AddField(
            model_name="order",
            name="tuppers_remaining",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.RunPython(copy_tuppers_requested_to_remaining),
    ]
