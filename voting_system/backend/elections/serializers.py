from rest_framework import serializers
from elections.models import Election, Candidate, ElectionStats
from voting.models import Vote

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'party', 'position', 'photo', 'bio', 'created_at']

class ElectionStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectionStats
        fields = ['total_registered_voters', 'total_votes_cast', 'turnout_percentage']

class ElectionSerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(many=True, read_only=True)
    stats = ElectionStatsSerializer(read_only=True)
    
    class Meta:
        model = Election
        fields = ['id', 'title', 'description', 'election_type', 'start_date', 
                  'end_date', 'status', 'candidates', 'stats', 'max_votes_per_voter', 
                  'is_anonymous', 'allow_write_ins', 'created_at']
        read_only_fields = ['created_at', 'stats']

class ElectionCreateSerializer(serializers.ModelSerializer):
    candidate_ids = serializers.ListField(child=serializers.UUIDField(), write_only=True)
    
    class Meta:
        model = Election
        fields = ['title', 'description', 'election_type', 'start_date', 'end_date', 
                  'candidate_ids', 'max_votes_per_voter', 'is_anonymous']
    
    def create(self, validated_data):
        candidate_ids = validated_data.pop('candidate_ids')
        election = Election.objects.create(**validated_data)
        candidates = Candidate.objects.filter(id__in=candidate_ids)
        election.candidates.set(candidates)
        ElectionStats.objects.create(election=election)
        return election
