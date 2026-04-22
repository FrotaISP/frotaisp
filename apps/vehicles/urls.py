# apps/vehicles/urls.py
from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    path('', views.VehicleListView.as_view(), name='list'),
    path('novo/', views.VehicleCreateView.as_view(), name='create'),
    path('documentos/', views.VehicleDocumentListView.as_view(), name='documents'),
    path('documentos/novo/', views.VehicleDocumentCreateView.as_view(), name='document_create'),
    path('documentos/<int:pk>/', views.VehicleDocumentDetailView.as_view(), name='document_detail'),
    path('documentos/<int:pk>/editar/', views.VehicleDocumentUpdateView.as_view(), name='document_update'),
    path('documentos/<int:pk>/excluir/', views.VehicleDocumentDeleteView.as_view(), name='document_delete'),
    path('checklists/', views.VehicleChecklistListView.as_view(), name='checklists'),
    path('checklists/novo/', views.VehicleChecklistCreateView.as_view(), name='checklist_create'),
    path('checklists/<int:pk>/', views.VehicleChecklistDetailView.as_view(), name='checklist_detail'),
    path('checklists/<int:pk>/editar/', views.VehicleChecklistUpdateView.as_view(), name='checklist_update'),
    path('checklists/<int:pk>/excluir/', views.VehicleChecklistDeleteView.as_view(), name='checklist_delete'),
    path('<int:pk>/', views.VehicleDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.VehicleUpdateView.as_view(), name='update'),
    path('<int:pk>/excluir/', views.VehicleDeleteView.as_view(), name='delete'),
]
