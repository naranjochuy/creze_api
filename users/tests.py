from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import pyotp

User = get_user_model()

class LoginViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="securepassword123"
        )
        self.login_url = reverse('login')

    def test_login_successful(self):
        data = {
            "email": "testuser@example.com",
            "password": "securepassword123"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['otp_activated'], self.user.otp_activated)
        self.assertEqual(response.data['otp_verified'], self.user.otp_verified)

    def test_login_invalid_credentials(self):
        data = {
            "email": "testuser@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Credenciales inválidas')

    def test_login_unregistered_user(self):
        data = {
            "email": "unregistered@example.com",
            "password": "anyPassword"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Credenciales inválidas')

    def test_login_with_otp_activated(self):
        self.user.otp_activated = True
        self.user.save()

        data = {
            "email": "testuser@example.com",
            "password": "securepassword123"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertTrue(response.data['otp_activated'])

    def test_login_missing_fields(self):
        data = {"email": "testuser@example.com"}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

class SignInViewTests(APITestCase):

    def setUp(self):
        self.url = reverse('signup')

    @patch('utils.common_functions.send_email')
    def test_signup_success(self, mock_send_email):
        data = {
            'email': 'newuser@test.com',
            'password': 'password123'
        }
        mock_send_email.return_value = None
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('utils.common_functions.send_email')
    def test_signup_duplicate_user(self, mock_send_email):
        User.objects.create_user(
            email='duplicate@example.com',
            password='DuplicatePassword123'
        )
        data = {
            'email': 'duplicate@example.com',
            'password': 'DuplicatePassword123'
        }
        mock_send_email.return_value = None
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('utils.common_functions.send_email')
    def test_signup_missing_fields(self, mock_send_email):
        data = {'email': 'newuser@test.com'}
        mock_send_email.return_value = None
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MFASetupViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpass123')
        token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer { token }')
        self.url = reverse('mfa-setup')

    def test_mfa_setup_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('otp_uri', response.data)

    def test_mfa_setup_already_verified(self):
        self.user.otp_verified = True
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Error en la petición', response.data['detail'])


class MFAValidateViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpass123')
        self.user.otp_secret = pyotp.random_base32()
        self.user.save()
        token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer { token }')
        self.url = reverse('mfa-validate')

    def test_mfa_validation_success_with_recovery_codes(self):
        totp = pyotp.TOTP(self.user.otp_secret)
        response = self.client.post(self.url, {'code': totp.now()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recovery_codes', response.data)

    def test_mfa_validation_success_without_recovery_codes(self):
        totp = pyotp.TOTP(self.user.otp_secret)
        self.user.generate_recovery_codes()
        response = self.client.post(self.url, {'code': totp.now()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data)

    def test_mfa_validation_invalid_code(self):
        response = self.client.post(self.url, {'code': '123456'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Código OTP inválido', response.data['code'])

    def test_mfa_validation_missing_fields(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('code', response.data)


class MFADisableViewTests(APITestCase):

    def setUp(self):
        user_data = {
            "email": 'test@example.com',
            "password": 'testpass123',
            "otp_activated": True,
            "otp_secret": pyotp.random_base32()
        }
        self.user = User.objects.create_user(**user_data)
        recovery_codes = self.user.generate_recovery_codes()
        self.code = recovery_codes[0]
        self.user.save()
        token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer { token }')
        self.url = reverse('mfa-disable')

    def test_mfa_disable_success(self):
        response = self.client.post(self.url, {'code': self.code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mfa_disable_not_activated(self):
        self.user.otp_activated = False
        self.user.save()
        response = self.client.post(self.url, {'code': 'recovery_code'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Error en la petición', response.data['detail'])

    def test_mfa_disable_missing_fields(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('code', response.data)


class MFAActivateViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpass123', otp_activated=False)
        token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer { token }')
        self.url = reverse('mfa-activate')

    def test_mfa_activation_success(self):
        self.user.save()
        self.user.refresh_from_db()
        response = self.client.post(self.url, {'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mfa_activation_already_activated(self):
        self.user.otp_activated = True
        self.user.save()
        self.user.refresh_from_db()
        response = self.client.post(self.url, {'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Error en la petición', response.data['detail'])

    def test_mfa_activation_missing_fields(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
