from eshop.models import User
import uuid
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings


def generate_token():
    return str(uuid.uuid4())


def generate_forgotPassword_token():
    return str(uuid.uuid4())


def send_verification_mail(user):
    token = user.email_verified_token
    verification_url = f"{settings.SITE_URL}/verify-email/?token={token}"
    subject = "Verify your email address"
    message = (
        f"hi {user.email}, click the link to verify your email: {verification_url}"
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user.email])
    

def send_verification_mail1(user):
    token = user.forgot_password_token
    verification_url = f"{settings.SITE_URL}/forgot-password-done/?token={token}"
    subject = "Verify your email address"
    message = (
        f"hi {user.email}, click the link to verify your email: {verification_url}"
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user.email])