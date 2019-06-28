from django.core.mail import send_mail
from django.urls import reverse


def send_confirmation_email(recipient_email, confirmation_token):
    subject = 'Confirm your email'
    confirmation_url = reverse('confirm', args=[confirmation_token])
    body = 'Click this %s to confirm your email' % confirmation_url
    send_mail(subject, body, 'pyramid@example.com', [recipient_email])
