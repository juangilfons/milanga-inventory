from django.contrib.admin.models import LogEntry
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import ActionLog

@receiver(post_save, sender=LogEntry)
def log_admin_action(sender, instance, **kwargs):
    user = instance.user
    action_type = 'ADMIN_ACTION'  # or define a new choice if needed
    description = f"Admin action: {instance.get_change_message()}"
    obj = instance.object_repr

    ActionLog.objects.create(
        user=user,
        user_role='ADMIN',
        action_type=action_type,
        object_repr=obj,
        action_description=description,
        action_time=timezone.now()
    )