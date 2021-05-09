from django.urls import path, include

from rest_framework.routers import SimpleRouter
from mobility_5g_rest_api import views

# Create a router and register our viewsets with it.
router = SimpleRouter()
router.register(r'event', views.EventViewSet)
router.register(r'climate', views.ClimateViewSet)
router.register(r'daily-inflow', views.DailyInflowViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('conditions_stats/', views.conditions_stats),
    path('carbon_footprint/', views.carbon_footprint),
    path('daily_excessive_speed/', views.daily_excessive_speed)
]