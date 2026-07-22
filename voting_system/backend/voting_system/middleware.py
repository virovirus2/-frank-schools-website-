import logging
from django.utils import timezone
from authentication.models import AuditLog

logger = logging.getLogger(__name__)

class AuditLoggingMiddleware:
    """Middleware to log all API requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log request
        if hasattr(request, 'user') and request.user.is_authenticated:
            action_map = {
                'POST': 'create',
                'PUT': 'update',
                'DELETE': 'delete',
                'GET': 'view'
            }
            action = action_map.get(request.method, 'unknown')
            
            try:
                AuditLog.objects.create(
                    voter=request.user,
                    action=action,
                    description=f"{request.method} {request.path}",
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    status='pending'
                )
            except Exception as e:
                logger.error(f"Error creating audit log: {e}")
        
        response = self.get_response(request)
        return response
    
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
