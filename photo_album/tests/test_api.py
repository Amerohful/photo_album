from io import BytesIO

from PIL import Image
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class PhotoApiTest(APITestCase):
    def setUp(self):
        call_command('load_fixtures')
        user1 = User.objects.get(id=1)
        user2 = User.objects.get(id=2)
        self.token1 = AccessToken.for_user(user1)
        self.token2 = AccessToken.for_user(user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')

    @staticmethod
    def get_image_file(filename='test.png', file_ext='png', size=(300, 300)):
        file_obj = BytesIO()
        image = Image.new('RGBA', size=size)
        image.save(file_obj, file_ext)
        file_obj.seek(0)
        return File(file_obj, filename)

    def test_create_photo(self):
        data = {
            'name': 'test photo',
            'photo': self.get_image_file(),
        }
        response = self.client.post(reverse('photo:list_create_photo'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['name'], data['name'])
        self.assertIsNotNone(response.json()['photo'])
        self.assertIsNotNone(response.json()['photo_thumbnail'])

    def test_thumbnail_photo(self):
        data = {
            'name': 'test thumbnail photo',
            'photo': self.get_image_file(),
        }
        response = self.client.post(reverse('photo:list_create_photo'), data)
        index = response.json()['photo_thumbnail'].find(settings.MEDIA_URL) + 1
        thumbnail_photo_path = response.json()['photo_thumbnail'][index:]
        with open(thumbnail_photo_path, 'rb') as file:
            thumbnail_photo = SimpleUploadedFile(
                name='test_thumbnail_image.png',
                content=file.read(),
                content_type='image/png'
            )
        width, height = get_image_dimensions(thumbnail_photo)
        self.assertEqual(width, 150)
        self.assertEqual(height, 150)

    def test_update_photo(self):
        create_data = {
            'name': 'test update photo',
            'photo': self.get_image_file(),
        }
        create_response = self.client.post(reverse('photo:list_create_photo'), create_data)
        update_data = {'name': 'new name'}
        update_response = self.client.put(
            reverse('photo:retrieve_update_photo', args=[create_response.json()['id']]),
            update_data
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.json()['name'], update_data['name'])

    def test_get_photo(self):
        create_data = {
            'name': 'test get photo',
            'photo': self.get_image_file(),
        }
        create_response = self.client.post(reverse('photo:list_create_photo'), create_data)
        get_response = self.client.get(reverse('photo:retrieve_update_photo',
                                               kwargs={'pk': create_response.json()['id']}))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(get_response.json()['photo'])
        self.assertIsNotNone(get_response.json()['photo_thumbnail'])

    def test_get_photo_another_author(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        create_data = {
            'name': 'test get photo',
            'photo': self.get_image_file(),
        }
        create_response = self.client.post(reverse('photo:list_create_photo'), create_data)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        get_response = self.client.get(reverse('photo:retrieve_update_photo',
                                               kwargs={'pk': create_response.json()['id']}))
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_photo(self):
        create_data = {
            'name': 'test get photo',
            'photo': self.get_image_file(),
        }
        list_url = reverse('photo:list_create_photo')
        self.client.post(list_url, create_data)
        list_response = self.client.get(list_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertIs(type(list_response.json()), list)
        self.assertIsNot(len(list_response.json()), 0)
        self.assertIsNotNone(list_response.json()[0]['photo'])
        self.assertIsNotNone(list_response.json()[0]['photo_thumbnail'])

    def test_get_personal_video(self):
        response = self.client.get(reverse('photo:get_video', kwargs={'personal': 'me'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json().get('video'))

    def test_get_public_video(self):
        response = self.client.get(reverse('photo:get_video', kwargs={'personal': 'all'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json().get('video'))
