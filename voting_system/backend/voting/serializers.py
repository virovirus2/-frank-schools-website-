from rest_framework import serializers
from voting.models import Vote, VoteVerification

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'election', 'candidate', 'timestamp', 'is_verified']
        read_only_fields = ['id', 'timestamp', 'is_verified']

class VoteCastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['election', 'candidate']
    
    def create(self, validated_data):
        # Add encryption and signature logic here
        return Vote.objects.create(**validated_data)

class VoteVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteVerification
        fields = ['verification_code', 'qr_code', 'created_at']
