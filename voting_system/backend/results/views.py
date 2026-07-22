from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from voting.models import Vote
from elections.models import Election
from results.models import Result, ResultsReport
from results.serializers import ResultSerializer, ResultsReportSerializer

class ResultsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        election_id = self.request.query_params.get('election_id')
        if election_id:
            return Result.objects.filter(election_id=election_id).order_by('-vote_count')
        return Result.objects.all()
    
    @action(detail=False, methods=['get'])
    def election_results(self, request):
        """Get results for a specific election"""
        election_id = request.query_params.get('election_id')
        
        try:
            election = Election.objects.get(id=election_id)
            
            # Check if election is closed
            if election.status != 'closed':
                return Response(
                    {'error': 'Election results not available yet'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            results = Result.objects.filter(election=election).order_by('-vote_count')
            serializer = ResultSerializer(results, many=True)
            
            return Response({
                'election': election.title,
                'total_votes': election.stats.total_votes_cast,
                'turnout': election.stats.turnout_percentage,
                'results': serializer.data
            }, status=status.HTTP_200_OK)
        except Election.DoesNotExist:
            return Response({'error': 'Election not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """Generate final results report (Admin only)"""
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        election_id = request.data.get('election_id')
        
        try:
            election = Election.objects.get(id=election_id)
            
            # Calculate results
            votes = Vote.objects.filter(election=election)
            total_votes = votes.count()
            
            # Get vote counts per candidate
            vote_counts = votes.values('candidate_id').annotate(count=Count('id'))
            
            # Get winner
            winner = None
            if vote_counts:
                winner_data = vote_counts.order_by('-count').first()
                winner_id = winner_data['candidate_id']
                winner = election.candidates.get(id=winner_id)
            
            # Create report
            report = ResultsReport.objects.create(
                election=election,
                total_votes=total_votes,
                total_registered=election.stats.total_registered_voters,
                turnout_percentage=(
                    (total_votes / election.stats.total_registered_voters * 100)
                    if election.stats.total_registered_voters > 0 else 0
                ),
                winner=winner,
                report_status='published',
                signed_by=request.user.username
            )
            
            serializer = ResultsReportSerializer(report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Election.DoesNotExist:
            return Response({'error': 'Election not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
