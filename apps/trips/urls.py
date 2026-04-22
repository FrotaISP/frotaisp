# apps/trips/urls.py
from django.urls import path
from . import views

app_name = 'trips'

urlpatterns = [
    path('', views.TripListView.as_view(), name='list'),
    path('<int:pk>/', views.TripDetailView.as_view(), name='detail'),
    path('nova/', views.TripCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.TripUpdateView.as_view(), name='update'),
    path('<int:pk>/excluir/', views.TripDeleteView.as_view(), name='delete'),
]