from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from eshop.models import User
from django.conf import settings


@receiver(post_save, sender=User)
def send_email_to_User(sender, instance, created, **kwargs):
    if created:
        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail("Welcome to our website", "Thankyou for signup", from_email, [instance.email],)