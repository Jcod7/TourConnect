from django.urls import path
from . import views

app_name = 'ecuador_data'

urlpatterns = [
    # Página principal
    path('', views.index, name='index'),
    
    # Provincias
    path('provincias/', views.ProvinciaListView.as_view(), name='provincia_list'),
    path('provincias/<int:pk>/', views.ProvinciaDetailView.as_view(), name='provincia_detail'),
    
    # Parques Nacionales
    path('parques/', views.ParqueListView.as_view(), name='parque_list'),
    path('parques/<int:pk>/', views.ParqueDetailView.as_view(), name='parque_detail'),
    
    # Sitios Patrimoniales
    path('sitios/', views.SitioListView.as_view(), name='sitio_list'),
    path('sitios/<int:pk>/', views.SitioDetailView.as_view(), name='sitio_detail'),
    
    # Plazas
    path('plazas/', views.PlazaListView.as_view(), name='plaza_list'),
    path('plazas/<int:pk>/', views.PlazaDetailView.as_view(), name='plaza_detail'),
    
    # APIs
    path('api/provincias/', views.api_provincias, name='api_provincias'),
    path('api/parques/', views.api_parques, name='api_parques'),
    
    # Búsqueda
    path('buscar/', views.search_results, name='search'),
    
]
