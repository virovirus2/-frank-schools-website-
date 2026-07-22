from django.urls import path, include
from rest_framework.routers import DefaultRouter
from elections.views import ElectionViewSet, CandidateViewSet

router = DefaultRouter()
router.register(r'elections', ElectionViewSet, basename='election', queryset=[])
router.register(r'candidates', CandidateViewSet, basename='candidate')

urlpatterns = [
    path('', include(router.urls)),
]
