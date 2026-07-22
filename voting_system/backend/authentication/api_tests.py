from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from authentication.models import Voter

class VoterRegistrationTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/voters/register/'
    
    def test_voter_registration_success(self):
        data = {
            'username': 'newvoter',
            'email': 'newvoter@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'national_id': '12345678',
            'phone': '1234567890'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_voter_registration_duplicate_username(self):
        Voter.objects.create_user(
            username='existingvoter',
            email='existing@example.com',
            password='testpass123',
            national_id='12345678'
        )
        data = {
            'username': 'existingvoter',
            'email': 'newvoter@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'national_id': '87654321'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_voter_registration_password_mismatch(self):
        data = {
            'username': 'newvoter',
            'email': 'newvoter@example.com',
            'password': 'SecurePass123!',
            'password2': 'DifferentPass123!',
            'national_id': '12345678'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
