from django.urls import path

from .views import (
    MobileChecklistListCreateView,
    MobileDashboardView,
    MobileDriverDocumentsView,
    MobileLocationUpdateView,
    MobileLoginView,
    MobileLogoutView,
    MobileMeView,
    MobileTripFinishView,
    MobileTripListCreateView,
)

urlpatterns = [
    path('auth/login/', MobileLoginView.as_view(), name='mobile_login'),
    path('auth/logout/', MobileLogoutView.as_view(), name='mobile_logout'),
    path('me/', MobileMeView.as_view(), name='mobile_me'),
    path('dashboard/', MobileDashboardView.as_view(), name='mobile_dashboard'),
    path('trips/', MobileTripListCreateView.as_view(), name='mobile_trips'),
    path('trips/<int:pk>/finish/', MobileTripFinishView.as_view(), name='mobile_trip_finish'),
    path('checklists/', MobileChecklistListCreateView.as_view(), name='mobile_checklists'),
    path('documents/', MobileDriverDocumentsView.as_view(), name='mobile_documents'),
    path('location/', MobileLocationUpdateView.as_view(), name='mobile_location'),
]
