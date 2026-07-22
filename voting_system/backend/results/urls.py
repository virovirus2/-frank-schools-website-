from django.urls import path, include
from rest_framework.routers import DefaultRouter
from results.views import ResultsViewSet

router = DefaultRouter()
router.register(r'results', ResultsViewSet, basename='result', queryset=[])

urlpatterns = [
    path('', include(router.urls)),
]
