from celery import shared_task
from django.db.models import Count
from django.utils import timezone
from elections.models import Election
from voting.models import Vote
from results.models import Result
import logging

logger = logging.getLogger(__name__)

@shared_task
def update_election_results(election_id):
    """Update results for an election"""
    try:
        election = Election.objects.get(id=election_id)
        votes = Vote.objects.filter(election=election)
        
        # Get vote counts per candidate
        vote_counts = votes.values('candidate_id').annotate(count=Count('id')).order_by('-count')
        
        total_votes = votes.count()
        
        # Update or create results
        rank = 1
        for vote_count in vote_counts:
            percentage = (vote_count['count'] / total_votes * 100) if total_votes > 0 else 0
            
            Result.objects.update_or_create(
                election_id=election_id,
                candidate_id=vote_count['candidate_id'],
                defaults={
                    'vote_count': vote_count['count'],
                    'percentage': percentage,
                    'rank': rank
                }
            )
            rank += 1
        
        # Update election stats
        election.stats.total_votes_cast = total_votes
        election.stats.turnout_percentage = (total_votes / election.stats.total_registered_voters * 100) if election.stats.total_registered_voters > 0 else 0
        election.stats.save()
        
        logger.info(f"Updated results for election {election_id}")
        return True
    except Exception as e:
        logger.error(f"Error updating results: {e}")
        return False

@shared_task
def close_election(election_id):
    """Automatically close election after end time"""
    try:
        election = Election.objects.get(id=election_id)
        if timezone.now() > election.end_date:
            election.status = 'closed'
            election.save()
            update_election_results.delay(election_id)
            logger.info(f"Closed election {election_id}")
            return True
    except Exception as e:
        logger.error(f"Error closing election: {e}")
        return False

@shared_task
def send_otp_email(voter_id, otp_code):
    """Send OTP via email"""
    try:
        from authentication.models import Voter
        from django.core.mail import send_mail
        
        voter = Voter.objects.get(id=voter_id)
        message = f"Your OTP is: {otp_code}. Valid for 5 minutes."
        send_mail(
            'Voting System OTP',
            message,
            'noreply@votingsystem.com',
            [voter.email],
            fail_silently=False,
        )
        logger.info(f"Sent OTP to {voter.email}")
        return True
    except Exception as e:
        logger.error(f"Error sending OTP email: {e}")
        return False
