from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserApiTest(APITestCase):
    def setUp(self):
        self.username = 'login_test'
        self.email = 'test@mail.com'
        self.password = 'password_test'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_register_new_user(self):
        register_data = {
            'username': 'register_test',
            'email': 'register_test@mail.com',
            'password': 'register_test_password',
        }
        response = self.client.post(reverse('user:register'), register_data)
        self.assertTrue(User.objects.filter(username=register_data['username']).exists())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['username'], register_data['username'])
        self.assertEqual(response.json()['subscription'], User.EmailSubscription.DAILY)

    def test_register_invalid_username(self):
        invalid_register_data = {
            'username': self.username,
            'email': 'valid_mail@mail.com',
            'password': self.password,
        }
        response = self.client.post(reverse('user:register'), invalid_register_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()['username'],
            ['A user with that username already exists.', ]
        )

    def test_login(self):
        response = self.client.post(
            reverse('user:token_obtain_pair'),
            {
                'username': self.username,
                'password': self.password,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())
        self.assertIsNotNone(response.json()['access'])
        self.assertIsNotNone(response.json()['refresh'])

    def test_login_invalid_data(self):
        response = self.client.post(
            reverse('user:token_obtain_pair'),
            {
                'username': self.username,
                'password': 'INVALID_PASSWORD',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictEqual(
            response.json(),
            {'detail': 'No active account found with the given credentials'}
        )

    def test_refresh_token(self):
        login_response = self.client.post(
            reverse('user:token_obtain_pair'),
            {
                'username': self.username,
                'password': self.password,
            }
        )
        refresh_token = login_response.json().get('refresh', str)
        refresh_response = self.client.post(
            reverse('user:token_refresh'),
            {'refresh': refresh_token},
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.json())
        self.assertIn('refresh', refresh_response.json())
        self.assertIsNotNone(refresh_response.json()['access'])
        self.assertIsNotNone(refresh_response.json()['refresh'])
