from django.db import models
from django.contrib.postgres.fields import ArrayField
from elections.models import Election, Candidate
from authentication.models import Voter
import uuid

class Vote(models.Model):
    """Encrypted vote model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(Voter, on_delete=models.SET_NULL, null=True, related_name='votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.SET_NULL, null=True, related_name='votes')
    encrypted_vote = models.TextField()  # Encrypted vote data
    digital_signature = models.TextField()  # Digital signature for verification
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    verification_hash = models.CharField(max_length=255, unique=True)  # For voter verification
    ip_address = models.GenericIPAddressField()
    device_fingerprint = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'votes'
        unique_together = ('election', 'voter')  # One vote per voter per election
        indexes = [
            models.Index(fields=['election', 'timestamp']),
            models.Index(fields=['voter']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"Vote in {self.election.title} - {self.timestamp}"

class VoteVerification(models.Model):
    """Vote verification receipt"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vote = models.OneToOneField(Vote, on_delete=models.CASCADE, related_name='verification')
    verification_code = models.CharField(max_length=255, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vote_verification'
    
    def __str__(self):
        return f"Verification for vote {self.vote.id}"
