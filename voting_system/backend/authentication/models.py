from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class Voter(AbstractUser):
    """Extended User model for voters"""
    VERIFICATION_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    voter_id = models.CharField(max_length=50, unique=True)
    national_id = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='pending')
    has_voted = models.BooleanField(default=False)
    is_eligible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_attempt = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'voters'
        indexes = [
            models.Index(fields=['national_id']),
            models.Index(fields=['voter_id']),
            models.Index(fields=['verification_status']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.voter_id})"

class OTPToken(models.Model):
    """One-Time Password for 2FA"""
    voter = models.OneToOneField(Voter, on_delete=models.CASCADE, related_name='otp_token')
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'otp_tokens'
    
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

class AuditLog(models.Model):
    """Immutable audit log for all voting activities"""
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('register', 'Register'),
        ('vote', 'Vote'),
        ('view_results', 'View Results'),
        ('admin_action', 'Admin Action'),
        ('election_created', 'Election Created'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voter = models.ForeignKey(Voter, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(max_length=20, default='success')
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['voter', 'timestamp']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.voter} - {self.timestamp}"
