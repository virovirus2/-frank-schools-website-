from rest_framework import serializers
from authentication.models import Voter, OTPToken, AuditLog
from django.contrib.auth.password_validation import validate_password

class VoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voter
        fields = ['id', 'username', 'voter_id', 'email', 'full_name', 'phone', 
                  'date_of_birth', 'address', 'verification_status', 'has_voted', 
                  'is_eligible', 'created_at']
        read_only_fields = ['has_voted', 'verification_status', 'created_at']

class VoterRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = Voter
        fields = ['username', 'email', 'password', 'password2', 'first_name', 
                  'last_name', 'national_id', 'phone', 'date_of_birth', 'address']
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs
    
    def create(self, validated_data):
        user = Voter.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            national_id=validated_data['national_id'],
            phone=validated_data.get('phone', ''),
            date_of_birth=validated_data.get('date_of_birth'),
            address=validated_data.get('address', ''),
            password=validated_data['password'],
        )
        return user

class OTPTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPToken
        fields = ['token', 'created_at', 'expires_at']

class AuditLogSerializer(serializers.ModelSerializer):
    voter_name = serializers.CharField(source='voter.full_name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = ['id', 'voter_name', 'action', 'description', 'ip_address', 
                  'timestamp', 'status']
        read_only_fields = ['id', 'timestamp']
