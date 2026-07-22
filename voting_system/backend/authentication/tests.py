from django.test import TestCase
from django.contrib.auth import get_user_model
from authentication.models import Voter, AuditLog

User = get_user_model()

class VoterModelTest(TestCase):
    def setUp(self):
        self.voter = Voter.objects.create_user(
            username='testvoter',
            email='test@example.com',
            password='testpass123',
            national_id='12345678'
        )
    
    def test_voter_creation(self):
        self.assertTrue(isinstance(self.voter, Voter))
        self.assertEqual(str(self.voter), self.voter.get_full_name())
    
    def test_voter_verification_status(self):
        self.assertEqual(self.voter.verification_status, 'pending')
        self.voter.verification_status = 'verified'
        self.voter.save()
        self.assertEqual(self.voter.verification_status, 'verified')

class AuditLogTest(TestCase):
    def setUp(self):
        self.voter = Voter.objects.create_user(
            username='testvoter',
            email='test@example.com',
            password='testpass123',
            national_id='12345678'
        )
    
    def test_audit_log_creation(self):
        log = AuditLog.objects.create(
            voter=self.voter,
            action='login',
            description='Test login',
            ip_address='127.0.0.1',
            status='success'
        )
        self.assertTrue(isinstance(log, AuditLog))
        self.assertEqual(log.action, 'login')
        self.assertIsNotNone(log.timestamp)
