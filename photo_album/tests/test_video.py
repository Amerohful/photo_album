from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from ..models import Photo

User = get_user_model()


class PhotoModelTest(TestCase):
    def setUp(self):
        call_command('load_fixtures')

    def test_generate_video(self):
        user = User.objects.get(id=1)
        photos = Photo.top_photos(user)
        video_url = Photo.generate_movie(photos)
        self.assertIsNotNone(video_url)
