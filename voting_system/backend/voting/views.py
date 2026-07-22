from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from voting.models import Vote, VoteVerification
from voting.serializers import VoteSerializer, VoteCastSerializer, VoteVerificationSerializer
from elections.models import Election
from authentication.models import AuditLog
from voting.encryption import EncryptionService
from voting.utils import get_client_ip, get_user_agent
import uuid

class VoteViewSet(viewsets.ModelViewSet):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Vote.objects.filter(voter=self.request.user)
    
    @action(detail=False, methods=['post'])
    def cast_vote(self, request):
        """Cast a vote"""
        voter = request.user
        election_id = request.data.get('election_id')
        candidate_id = request.data.get('candidate_id')
        
        try:
            # Check if election exists and is active
            election = Election.objects.get(id=election_id)
            if election.status != 'active':
                return Response({'error': 'Election is not active'}, status=status.HTTP_400_BAD_REQUEST)
            
            if timezone.now() < election.start_date or timezone.now() > election.end_date:
                return Response({'error': 'Voting is not available now'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if voter has already voted
            if Vote.objects.filter(election=election, voter=voter).exists():
                return Response({'error': 'You have already voted in this election'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check voter eligibility
            if not voter.is_eligible or voter.verification_status != 'verified':
                return Response({'error': 'You are not eligible to vote'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Encrypt the vote
            encryption_service = EncryptionService()
            vote_data = {'candidate_id': str(candidate_id), 'election_id': str(election_id)}
            encrypted_vote = encryption_service.encrypt(vote_data)
            digital_signature = encryption_service.sign(encrypted_vote)
            
            # Create vote record
            vote = Vote.objects.create(
                election=election,
                voter=voter,
                candidate_id=candidate_id,
                encrypted_vote=encrypted_vote,
                digital_signature=digital_signature,
                verification_hash=str(uuid.uuid4()),
                ip_address=get_client_ip(request),
                device_fingerprint=request.data.get('device_fingerprint', ''),
                is_verified=True
            )
            
            # Create verification receipt
            verification = VoteVerification.objects.create(
                vote=vote,
                verification_code=str(uuid.uuid4())
            )
            
            # Update voter
            voter.has_voted = True
            voter.save()
            
            # Log the vote
            AuditLog.objects.create(
                voter=voter,
                action='vote',
                description=f'Vote cast in {election.title}',
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                status='success'
            )
            
            return Response({
                'message': 'Vote cast successfully',
                'verification_code': verification.verification_code,
                'timestamp': vote.timestamp
            }, status=status.HTTP_201_CREATED)
        
        except Election.DoesNotExist:
            return Response({'error': 'Election not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def verify_vote(self, request):
        """Verify vote using verification code"""
        verification_code = request.query_params.get('code')
        
        try:
            verification = VoteVerification.objects.get(verification_code=verification_code)
            vote = verification.vote
            
            return Response({
                'verified': True,
                'election': vote.election.title,
                'timestamp': vote.timestamp,
                'is_valid': vote.is_verified
            }, status=status.HTTP_200_OK)
        except VoteVerification.DoesNotExist:
            return Response({'error': 'Invalid verification code'}, status=status.HTTP_404_NOT_FOUND)
