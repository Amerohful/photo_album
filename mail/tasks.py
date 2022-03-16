from celery import shared_task

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .models import MailTemplate

User = get_user_model()


def send_multiply_mail(recipient_list, mail_type='notify'):
    """ Send multiply mails
    """
    mail_template = MailTemplate.objects.get(type=mail_type)
    send_mail(
        mail_template.subject,
        mail_template.body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
    )


@shared_task
def send_daily_notification():
    """ Send mails everyday
    """
    users = User.objects.filter(subscription=User.EmailSubscription.DAILY).values('email')
    users_email = [user['email'] for user in users]
    send_multiply_mail(users_email, 'notify')


@shared_task
def send_monthly_notification():
    """ Send mails every month
    """
    users = User.objects.filter(subscription=User.EmailSubscription.MONTHLY).values('email')
    users_email = [user['email'] for user in users]
    send_multiply_mail(users_email, 'notify')
