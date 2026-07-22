from django.db import models
import uuid

class Candidate(models.Model):
    """Candidate model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    party = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='candidates/', null=True, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'candidates'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Election(models.Model):
    """Election model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    election_type = models.CharField(max_length=100)  # President, Governor, etc
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    candidates = models.ManyToManyField(Candidate, related_name='elections')
    max_votes_per_voter = models.IntegerField(default=1)
    is_anonymous = models.BooleanField(default=True)
    allow_write_ins = models.BooleanField(default=False)
    created_by = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'elections'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return self.title

class ElectionStats(models.Model):
    """Election statistics"""
    election = models.OneToOneField(Election, on_delete=models.CASCADE, related_name='stats')
    total_registered_voters = models.IntegerField(default=0)
    total_votes_cast = models.IntegerField(default=0)
    turnout_percentage = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'election_stats'
    
    def __str__(self):
        return f"Stats for {self.election.title}"
