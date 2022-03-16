import os
import time

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.resize import resize
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Photo(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=150)
    photo = models.ImageField(verbose_name=_('photo'), upload_to='photos')
    photo_webp = ImageSpecField(source='photo', format='webp')
    photo_thumbnail = ImageSpecField(source='photo',
                                     processors=[ResizeToFill(150, 150), ],
                                     options={'quality': 60})
    view_counter = models.IntegerField(verbose_name=_('view counter'), default=0)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(_('date created'), auto_now_add=True)

    def add_view(self):
        self.view_counter += 1
        self.save()

    @classmethod
    def top_photos(cls, author=None):
        """ Return top 10 photos or top 10 photos by author
        """
        if author is None:
            return cls.objects.order_by('-view_counter')[:10]
        return cls.objects.filter(author=author).order_by('-view_counter')[:10]

    @staticmethod
    def generate_movie(photos):
        """ Generate video from photos
        """
        filename = f'{int(time.time())}.webm'
        frames = [resize(ImageClip(
            photo.photo.path,
            duration=1
        ), height=600, width=600) for photo in photos]
        clip = concatenate_videoclips(frames, method='compose')
        path = os.path.join(settings.MEDIA_ROOT, 'videos', filename)
        clip.write_videofile(path, fps=24)

        return os.path.join(settings.MEDIA_URL, 'videos', filename)
