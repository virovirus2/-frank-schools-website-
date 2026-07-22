from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.contrib.auth.hashers import make_password
import pyotp
import random
from authentication.models import Voter, OTPToken, AuditLog
from authentication.serializers import VoterSerializer, VoterRegistrationSerializer, OTPTokenSerializer, AuditLogSerializer
from voting.utils import get_client_ip, get_user_agent

class VoterViewSet(viewsets.ModelViewSet):
    queryset = Voter.objects.all()
    serializer_class = VoterSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Register a new voter"""
        serializer = VoterRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                voter = serializer.save()
                
                # Log registration
                AuditLog.objects.create(
                    voter=voter,
                    action='register',
                    description='New voter registered',
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    status='success'
                )
                
                # Generate voter ID
                voter.voter_id = f"VID-{voter.id}-{random.randint(10000, 99999)}"
                voter.verification_status = 'pending'
                voter.save()
                
                refresh = RefreshToken.for_user(voter)
                return Response({
                    'message': 'Registration successful',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'voter_id': voter.voter_id
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def send_otp(self, request):
        """Send OTP to voter"""
        voter = request.user
        try:
            # Generate 6-digit OTP
            otp_code = str(random.randint(100000, 999999))
            
            # Delete existing OTP
            OTPToken.objects.filter(voter=voter).delete()
            
            # Create new OTP
            otp_token = OTPToken.objects.create(
                voter=voter,
                token=otp_code,
                expires_at=timezone.now() + timezone.timedelta(minutes=5)
            )
            
            # TODO: Send OTP via SMS or Email
            # send_otp_email(voter.email, otp_code)
            
            return Response({
                'message': 'OTP sent successfully',
                'expires_in': 300  # 5 minutes
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def verify_otp(self, request):
        """Verify OTP"""
        voter = request.user
        otp_code = request.data.get('otp')
        
        try:
            otp_token = OTPToken.objects.get(voter=voter)
            
            if not otp_token.is_valid():
                return Response({'error': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
            
            if otp_token.token != otp_code:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark OTP as used
            otp_token.is_used = True
            otp_token.used_at = timezone.now()
            otp_token.save()
            
            # Update voter
            voter.verification_status = 'verified'
            voter.save()
            
            AuditLog.objects.create(
                voter=voter,
                action='login',
                description='OTP verified successfully',
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                status='success'
            )
            
            return Response({
                'message': 'OTP verified successfully',
                'verification_status': voter.verification_status
            }, status=status.HTTP_200_OK)
        except OTPToken.DoesNotExist:
            return Response({'error': 'OTP not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        """Get voter profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def audit_logs(self, request):
        """Get voter's audit logs"""
        logs = AuditLog.objects.filter(voter=request.user).order_by('-timestamp')[:50]
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)
