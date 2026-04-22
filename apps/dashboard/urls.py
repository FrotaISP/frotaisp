# apps/dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='index'),
    path('rastreamento/', views.tracking_map_view, name='tracking'),
    path('rastreamento/dados/', views.tracking_positions_api, name='tracking_positions'),
]