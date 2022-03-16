from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):

    class EmailSubscription(models.TextChoices):
        """ Type of email subscription
        """
        DAILY = 'daily', _('Daily')
        MONTHLY = 'monthly', _('Monthly')

    subscription = models.CharField(
        verbose_name=_('subscription'),
        max_length=11,
        choices=EmailSubscription.choices,
        default=EmailSubscription.DAILY
    )

    def __str__(self):
        return f'{self.username} {self.email}'
