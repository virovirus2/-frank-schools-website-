from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
import pyotp
import random
import logging
from authentication.models import Voter, OTPToken, AuditLog
from authentication.serializers import VoterSerializer, VoterRegistrationSerializer, OTPTokenSerializer, AuditLogSerializer
from voting.utils import get_client_ip, get_user_agent

logger = logging.getLogger('audit')

class VoterViewSet(viewsets.ModelViewSet):
    queryset = Voter.objects.all()
    serializer_class = VoterSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['voter_id', 'email', 'full_name']
    ordering_fields = ['created_at', 'voter_id']
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Register a new voter with validation"""
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
                logger.info(f"Voter registered: {voter.username}")
                
                # Generate voter ID
                voter.voter_id = f"VID-{voter.id}-{random.randint(10000, 99999)}"
                voter.verification_status = 'pending'
                voter.save()
                
                # Generate tokens
                refresh = RefreshToken.for_user(voter)
                
                return Response({
                    'message': 'Registration successful. Check your email for verification.',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'voter_id': voter.voter_id
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def send_otp(self, request):
        """Send OTP to voter's email"""
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
            
            # Send OTP via email
            try:
                send_mail(
                    'Your Voting System OTP',
                    f'Your OTP is: {otp_code}. Valid for 5 minutes.',
                    'noreply@votingsystem.com',
                    [voter.email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"Failed to send OTP email: {str(e)}")
            
            logger.info(f"OTP sent to {voter.email}")
            
            return Response({
                'message': 'OTP sent successfully',
                'expires_in': 300  # 5 minutes
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"OTP send error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def verify_otp(self, request):
        """Verify OTP and activate account"""
        voter = request.user
        otp_code = request.data.get('otp')
        
        if not otp_code:
            return Response({'error': 'OTP code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            otp_token = OTPToken.objects.get(voter=voter)
            
            if not otp_token.is_valid():
                logger.warning(f"OTP expired for user: {voter.username}")
                return Response({'error': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
            
            if otp_token.token != otp_code:
                logger.warning(f"Invalid OTP attempt for user: {voter.username}")
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
            
            logger.info(f"OTP verified for user: {voter.username}")
            
            return Response({
                'message': 'OTP verified successfully',
                'verification_status': voter.verification_status
            }, status=status.HTTP_200_OK)
        except OTPToken.DoesNotExist:
            logger.error(f"OTP not found for user: {voter.username}")
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
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """Change voter password"""
        voter = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not voter.check_password(old_password):
            return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)
        
        voter.set_password(new_password)
        voter.save()
        
        logger.info(f"Password changed for user: {voter.username}")
        
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
