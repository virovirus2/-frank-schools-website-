from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from elections.models import Election, Candidate, ElectionStats
from elections.serializers import ElectionSerializer, ElectionCreateSerializer, CandidateSerializer
from authentication.models import AuditLog
from voting.utils import get_client_ip, get_user_agent

class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'party', 'position']
    ordering_fields = ['name', 'created_at']

class ElectionViewSet(viewsets.ModelViewSet):
    serializer_class = ElectionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'election_type']
    ordering_fields = ['start_date', 'created_at']
    
    def get_queryset(self):
        queryset = Election.objects.all()
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create new election (Admin only)"""
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ElectionCreateSerializer(data=request.data)
        if serializer.is_valid():
            election = serializer.save(created_by=request.user.username)
            
            AuditLog.objects.create(
                voter=request.user,
                action='election_created',
                description=f'Election created: {election.title}',
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                status='success'
            )
            
            return Response(
                ElectionSerializer(election).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate an election"""
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        election = self.get_object()
        election.status = 'active'
        election.save()
        
        return Response({'message': 'Election activated'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close an election"""
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        election = self.get_object()
        election.status = 'closed'
        election.save()
        
        return Response({'message': 'Election closed'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get election statistics"""
        election = self.get_object()
        stats = election.stats
        
        return Response({
            'total_registered_voters': stats.total_registered_voters,
            'total_votes_cast': stats.total_votes_cast,
            'turnout_percentage': stats.turnout_percentage,
        }, status=status.HTTP_200_OK)
