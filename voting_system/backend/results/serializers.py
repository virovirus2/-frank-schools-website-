from rest_framework import serializers
from results.models import Result, ResultsReport

class ResultSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.name', read_only=True)
    
    class Meta:
        model = Result
        fields = ['id', 'candidate_name', 'vote_count', 'percentage', 'rank']

class ResultsReportSerializer(serializers.ModelSerializer):
    winner_name = serializers.CharField(source='winner.name', read_only=True)
    election_title = serializers.CharField(source='election.title', read_only=True)
    
    class Meta:
        model = ResultsReport
        fields = ['id', 'election_title', 'total_votes', 'total_registered', 
                  'turnout_percentage', 'invalid_votes', 'winner_name', 
                  'report_status', 'published_at']
