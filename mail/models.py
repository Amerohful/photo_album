from django.db import models
from django.utils.translation import gettext_lazy as _


class MailTemplate(models.Model):
    type = models.CharField(_('type'), max_length=100, unique=True)
    subject = models.CharField(_('mail title'), max_length=255)
    body = models.TextField(_('mail body'))
