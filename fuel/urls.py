# apps/fuel/urls.py
from django.urls import path
from . import views

app_name = 'fuel'

urlpatterns = [
    path('', views.FuelRecordListView.as_view(), name='list'),
    path('<int:pk>/', views.FuelRecordDetailView.as_view(), name='detail'),
    path('novo/', views.FuelRecordCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.FuelRecordUpdateView.as_view(), name='update'),
    path('<int:pk>/excluir/', views.FuelRecordDeleteView.as_view(), name='delete'),
]