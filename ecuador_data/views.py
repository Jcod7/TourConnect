from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.core.cache import cache
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.utils import timezone
from .models import Provincia, ParqueNacional, SitioPatrimonial, Plaza
from .sparql_services import DataSyncService
from .optimized_services import OptimizedDataSyncService
import logging

logger = logging.getLogger(__name__)


def index(request):
    """Vista principal del sitio - OPTIMIZADA con cache"""
    # Cache de estadísticas para renderizado instantáneo
    cache_key = 'dashboard_stats'
    context = cache.get(cache_key)
    
    if context is None:
        logger.info("Cache miss - generando estadísticas dashboard")
        context = {
            'total_provincias': Provincia.objects.count(),
            'total_parques': ParqueNacional.objects.count(), 
            'total_sitios': SitioPatrimonial.objects.count(),
            'total_plazas': Plaza.objects.count(),
        }
        cache.set(cache_key, context, 3600)  # Cache 1 hora
    else:
        logger.info("Cache hit - estadísticas dashboard desde cache")
    
    # Trigger async sync only if needed (no blocking)
    _trigger_background_sync_if_needed()
    
    return render(request, 'ecuador_data/index.html', context)


class ProvinciaListView(ListView):
    """Vista de lista de provincias - OPTIMIZADA"""
    model = Provincia
    template_name = 'ecuador_data/provincia_list.html'
    context_object_name = 'provincias'
    paginate_by = 12

    def get(self, request, *args, **kwargs):
        # Sync inteligente: solo si es necesario, sin bloquear
        _trigger_background_sync_if_needed('provincias')
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        """Queryset optimizado con select_related si fuera necesario"""
        return Provincia.objects.all().order_by('nombre')


class ProvinciaDetailView(DetailView):
    """Vista de detalle de provincia"""
    model = Provincia
    template_name = 'ecuador_data/provincia_detail.html'
    context_object_name = 'provincia'


class ParqueListView(ListView):
    """Vista de lista de parques nacionales - OPTIMIZADA"""
    model = ParqueNacional
    template_name = 'ecuador_data/parque_list.html'
    context_object_name = 'parques'
    paginate_by = 12

    def get(self, request, *args, **kwargs):
        _trigger_background_sync_if_needed('parques')
        return super().get(request, *args, **kwargs)


class ParqueDetailView(DetailView):
    """Vista de detalle de parque nacional"""
    model = ParqueNacional
    template_name = 'ecuador_data/parque_detail.html'
    context_object_name = 'parque'


class SitioListView(ListView):
    """Vista de lista de sitios patrimoniales - OPTIMIZADA"""
    model = SitioPatrimonial
    template_name = 'ecuador_data/sitio_list.html'
    context_object_name = 'sitios'
    paginate_by = 12

    def get(self, request, *args, **kwargs):
        _trigger_background_sync_if_needed('sitios')
        return super().get(request, *args, **kwargs)


class SitioDetailView(DetailView):
    """Vista de detalle de sitio patrimonial"""
    model = SitioPatrimonial
    template_name = 'ecuador_data/sitio_detail.html'
    context_object_name = 'sitio'


class PlazaListView(ListView):
    """Vista de lista de plazas - OPTIMIZADA"""
    model = Plaza
    template_name = 'ecuador_data/plaza_list.html'
    context_object_name = 'plazas'
    paginate_by = 12

    def get(self, request, *args, **kwargs):
        _trigger_background_sync_if_needed('plazas')
        return super().get(request, *args, **kwargs)


class PlazaDetailView(DetailView):
    """Vista de detalle de plaza"""
    model = Plaza
    template_name = 'ecuador_data/plaza_detail.html'
    context_object_name = 'plaza'


def api_provincias(request):
    """API REST para provincias"""
    provincias = Provincia.objects.all()
    data = []
    for provincia in provincias:
        data.append({
            'id': provincia.id,
            'nombre': provincia.nombre,
            'capital': provincia.capital,
            'poblacion': provincia.poblacion,
            'area': provincia.area,
            'latitud': provincia.latitud,
            'longitud': provincia.longitud,
            'imagen_url': provincia.imagen_url,
        })
    return JsonResponse({'provincias': data})


def api_parques(request):
    """API REST para parques nacionales"""
    parques = ParqueNacional.objects.all()
    data = []
    for parque in parques:
        data.append({
            'id': parque.id,
            'nombre': parque.nombre,
            'area': parque.area,
            'provincia': parque.provincia,
            'latitud': parque.latitud,
            'longitud': parque.longitud,
            'imagen_url': parque.imagen_url,
        })
    return JsonResponse({'parques': data})


# Funciones auxiliares optimizadas
def _trigger_background_sync_if_needed(sync_type: str = 'all'):
    """Trigger background sync only if data is stale - NO BLOCKING"""
    try:
        sync_service = OptimizedDataSyncService()
        
        if sync_type == 'all':
            should_sync = sync_service.should_sync('general')
        else:
            should_sync = sync_service.should_sync(sync_type)
        
        if should_sync:
            logger.info(f"Disparando sync background para {sync_type}")
            # En producción: usar Celery task aquí
            # sync_sparql_data.delay(sync_type)
            
            # Para desarrollo: sync directo pero loggeado
            if sync_type == 'provincias':
                sync_service.sync_provincias_concurrent()
            elif sync_type == 'parques':
                sync_service.sync_parques_nacionales()
            # elif sync_type == 'all':
            #     sync_service.sync_all_optimized()
        else:
            logger.info(f"Sync {sync_type} omitido - datos recientes")
            
    except Exception as e:
        logger.error(f"Error en background sync {sync_type}: {e}")

def search_results(request):
    """Vista de búsqueda unificada para todos los tipos de contenido"""
    query = request.GET.get('q', '').strip()
    
    context = {
        'query': query,
        'sitios': [],
        'parques': [],
        'plazas': [],
        'provincias': [],
        'total_results': 0
    }
    
    if query and len(query) >= 2:  # Mínimo 2 caracteres para buscar
        # Buscar en sitios patrimoniales
        sitios = SitioPatrimonial.objects.filter(
            nombre__icontains=query
        ).order_by('nombre')[:10]  # Limitar a 10 resultados por tipo
        
        # Buscar en parques nacionales
        parques = ParqueNacional.objects.filter(
            nombre__icontains=query
        ).order_by('nombre')[:10]
        
        # Buscar en plazas
        plazas = Plaza.objects.filter(
            nombre__icontains=query
        ).order_by('nombre')[:10]
        
        # Buscar en provincias
        provincias = Provincia.objects.filter(
            nombre__icontains=query
        ).order_by('nombre')[:10]
        
        context.update({
            'sitios': sitios,
            'parques': parques,
            'plazas': plazas,
            'provincias': provincias,
            'total_results': len(sitios) + len(parques) + len(plazas) + len(provincias)
        })
    
    return render(request, 'ecuador_data/search_results.html', context)


# Vistas de sincronización SPARQL manual (para admin)