from django.db import models
from elections.models import Election, Candidate
import uuid

class Result(models.Model):
    """Election results"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='results')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='results')
    vote_count = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    rank = models.IntegerField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'results'
        unique_together = ('election', 'candidate')
        ordering = ['-vote_count']
        indexes = [
            models.Index(fields=['election']),
        ]
    
    def __str__(self):
        return f"{self.candidate.name} - {self.election.title} ({self.vote_count} votes)"

class ResultsReport(models.Model):
    """Final election results report"""
    REPORT_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.OneToOneField(Election, on_delete=models.CASCADE, related_name='final_report')
    total_votes = models.IntegerField(default=0)
    total_registered = models.IntegerField(default=0)
    turnout_percentage = models.FloatField(default=0.0)
    invalid_votes = models.IntegerField(default=0)
    winner = models.ForeignKey(Candidate, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_elections')
    report_status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default='draft')
    pdf_report = models.FileField(upload_to='reports/', null=True, blank=True)
    excel_report = models.FileField(upload_to='reports/', null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    signed_by = models.CharField(max_length=200, blank=True)
    digital_signature = models.TextField(blank=True)
    
    class Meta:
        db_table = 'results_reports'
    
    def __str__(self):
        return f"Report for {self.election.title}"
