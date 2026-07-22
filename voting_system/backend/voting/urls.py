from django.urls import path, include
from rest_framework.routers import DefaultRouter
from voting.views import VoteViewSet

router = DefaultRouter()
router.register(r'votes', VoteViewSet, basename='vote', queryset=[])

urlpatterns = [
    path('', include(router.urls)),
]
