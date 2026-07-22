from django.urls import path, include
from rest_framework.routers import DefaultRouter
from authentication.views import VoterViewSet

router = DefaultRouter()
router.register(r'voters', VoterViewSet, basename='voter')

urlpatterns = [
    path('', include(router.urls)),
]
