"""
Servicios SPARQL optimizados con cache y procesamiento concurrente
"""
import logging
import time
import unicodedata
import re
from typing import Dict, List, Optional, Any
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.cache import cache, caches
from django.conf import settings
from django.utils import timezone
from .sparql_services import WikidataService, DBpediaService, DataSyncService

logger = logging.getLogger(__name__)

class TextProcessor:
    """Procesador de texto optimizado con cache"""
    
    # Compilar regex una sola vez para mejor rendimiento
    CLEANUP_PATTERN = re.compile(r'[^a-zA-Z0-9\s]')
    NORMALIZE_PATTERN = re.compile(r'\s+')
    
    @lru_cache(maxsize=200)
    def normalize_name(self, name: str) -> str:
        """Normalización optimizada con LRU cache"""
        if not name:
            return ""
        
        # Normalización unicode
        name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
        
        # Limpiar y normalizar
        name = name.lower()
        name = name.replace('provincia', '').replace('province', '').replace('ecuador', '')
        name = name.replace('del', '').replace('de', '').replace('la', '').replace('el', '')
        name = name.replace('los', '').replace('las', '').replace('islas', '')
        name = self.CLEANUP_PATTERN.sub('', name)
        name = self.NORMALIZE_PATTERN.sub('', name.strip())
        
        return name

class CachedWikidataService(WikidataService):
    """WikidataService con cache inteligente"""
    
    def __init__(self):
        super().__init__()
        self.sparql_cache = caches['sparql']
    
    def get_provincias_detalladas(self) -> Optional[List[Dict[str, Any]]]:
        cache_key = 'wikidata_provincias_detalladas'
        results = self.sparql_cache.get(cache_key)
        
        if results is None:
            logger.info("Cache miss - consultando Wikidata para provincias")
            results = super().get_provincias_detalladas()
            if results:
                self.sparql_cache.set(cache_key, results, 86400)  # 24 horas
                logger.info(f"Cached {len(results)} provincias en SPARQL cache")
        else:
            logger.info(f"Cache hit - {len(results)} provincias desde cache")
        
        return results
    
    def get_parques_nacionales(self) -> Optional[List[Dict[str, Any]]]:
        cache_key = 'wikidata_parques_nacionales'
        results = self.sparql_cache.get(cache_key)
        
        if results is None:
            logger.info("Cache miss - consultando Wikidata para parques")
            results = super().get_parques_nacionales() 
            if results:
                self.sparql_cache.set(cache_key, results, 86400)
                logger.info(f"Cached {len(results)} parques en SPARQL cache")
        else:
            logger.info(f"Cache hit - {len(results)} parques desde cache")
        
        return results
    
    def get_sitios_patrimoniales(self) -> Optional[List[Dict[str, Any]]]:
        cache_key = 'wikidata_sitios_patrimoniales'
        results = self.sparql_cache.get(cache_key)
        
        if results is None:
            logger.info("Cache miss - consultando Wikidata para sitios")
            results = super().get_sitios_patrimoniales()
            if results:
                self.sparql_cache.set(cache_key, results, 86400)
                logger.info(f"Cached {len(results)} sitios en SPARQL cache")
        else:
            logger.info(f"Cache hit - {len(results)} sitios desde cache")
        
        return results
    
    def get_plazas(self) -> Optional[List[Dict[str, Any]]]:
        cache_key = 'wikidata_plazas'
        results = self.sparql_cache.get(cache_key)
        
        if results is None:
            logger.info("Cache miss - consultando Wikidata para plazas")
            results = super().get_plazas()
            if results:
                self.sparql_cache.set(cache_key, results, 86400)
                logger.info(f"Cached {len(results)} plazas en SPARQL cache")
        else:
            logger.info(f"Cache hit - {len(results)} plazas desde cache")
        
        return results

class CachedDBpediaService(DBpediaService):
    """DBpediaService con cache inteligente"""
    
    def __init__(self):
        super().__init__()
        self.sparql_cache = caches['sparql']
    
    def get_provincias_banderas(self) -> Optional[List[Dict[str, Any]]]:
        cache_key = 'dbpedia_provincias_banderas'
        results = self.sparql_cache.get(cache_key)
        
        if results is None:
            logger.info("Cache miss - consultando DBpedia para banderas")
            results = super().get_provincias_banderas()
            if results:
                self.sparql_cache.set(cache_key, results, 86400)
                logger.info(f"Cached {len(results)} banderas en SPARQL cache")
        else:
            logger.info(f"Cache hit - {len(results)} banderas desde cache")
        
        return results

class OptimizedDataSyncService:
    """Servicio de sincronización optimizado con concurrencia y cache"""
    
    def __init__(self):
        self.wikidata = CachedWikidataService()
        self.dbpedia = CachedDBpediaService()
        self.text_processor = TextProcessor()
        self.default_cache = cache
        self.sparql_cache = caches['sparql']
    
    def should_sync(self, sync_type: str) -> bool:
        """Determina si necesita sincronizar basado en última actualización Y si la BD está vacía"""
        # Verificar si la BD está vacía para este tipo de datos
        if self._is_database_empty(sync_type):
            logger.info(f"BD vacía para {sync_type} - forzando sincronización")
            return True
        
        # Verificar tiempo desde última sincronización
        last_sync_key = f'last_sync_{sync_type}'
        last_sync = self.default_cache.get(last_sync_key)
        
        if not last_sync:
            return True
        
        time_since_sync = (timezone.now() - last_sync).total_seconds()
        sync_interval = getattr(settings, 'SPARQL_SYNC_INTERVAL', 21600)  # 6 horas
        
        return time_since_sync > sync_interval
    
    def _is_database_empty(self, sync_type: str) -> bool:
        """Verifica si la base de datos está vacía para el tipo específico"""
        from .models import Provincia, ParqueNacional, SitioPatrimonial, Plaza
        
        try:
            if sync_type in ['provincias', 'general']:
                return Provincia.objects.count() == 0
            elif sync_type == 'parques':
                return ParqueNacional.objects.count() == 0
            elif sync_type == 'sitios':
                return SitioPatrimonial.objects.count() == 0
            elif sync_type == 'plazas':
                return Plaza.objects.count() == 0
            else:
                # Para 'general', verificar si cualquier tabla está vacía
                return (Provincia.objects.count() == 0 or 
                       ParqueNacional.objects.count() == 0 or 
                       SitioPatrimonial.objects.count() == 0 or 
                       Plaza.objects.count() == 0)
        except Exception as e:
            logger.error(f"Error verificando BD vacía para {sync_type}: {e}")
            return True  # En caso de error, forzar sync
    
    def mark_synced(self, sync_type: str):
        """Marca el tipo de sincronización como completado"""
        self.default_cache.set(f'last_sync_{sync_type}', timezone.now(), 86400)
    
    def sync_provincias_concurrent(self) -> Dict[str, Any]:
        """Sincronización concurrente de provincias con múltiples fuentes"""
        from .models import Provincia
        
        result = {"created": 0, "updated": 0, "errors": []}
        
        if not self.should_sync('provincias'):
            logger.info("Sincronización de provincias omitida - datos recientes en cache")
            return result
        
        start_time = time.time()
        logger.info("Iniciando sincronización concurrente de provincias")
        
        # Ejecutar consultas en paralelo usando ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Lanzar consultas concurrentemente
            futures = {
                'wikidata': executor.submit(self.wikidata.get_provincias_detalladas),
                'banderas': executor.submit(self.dbpedia.get_provincias_banderas),
                'cantones': executor.submit(self._get_provincias_cantones_cached)
            }
            
            # Recopilar resultados
            results = {}
            for name, future in futures.items():
                try:
                    results[name] = future.result(timeout=30)  # 30s timeout
                    logger.info(f"Consulta {name} completada")
                except Exception as e:
                    logger.error(f"Error en consulta {name}: {e}")
                    results[name] = None
        
        query_time = time.time() - start_time
        logger.info(f"Consultas SPARQL completadas en {query_time:.2f}s")
        
        # Procesar datos si las consultas fueron exitosas
        wikidata_results = results.get('wikidata')
        if not wikidata_results:
            result["errors"].append("No se pudieron obtener datos de Wikidata")
            return result
        
        # Preparar datos complementarios
        dbpedia_flags = self._process_banderas(results.get('banderas', []))
        provincia_cantones = results.get('cantones', {})
        
        # Procesar y actualizar provincias
        process_start = time.time()
        provincias_to_update = []
        
        for item in wikidata_results:
            try:
                nombre = item.get("provinciaLabel", {}).get("value", "")
                if not nombre:
                    continue
                
                # Procesar coordenadas optimizado
                latitud, longitud = self._parse_coordinates_optimized(
                    item.get("coordenadas", {}).get("value", "")
                )
                
                # Buscar bandera optimizado
                bandera_url = self._get_best_flag_url(item, dbpedia_flags, nombre)
                
                # Asociar cantones optimizado
                cantones = self._get_cantones_for_provincia(provincia_cantones, nombre)
                
                # Usar get_or_create para eficiencia
                provincia, created = Provincia.objects.get_or_create(
                    nombre=nombre,
                    defaults={
                        'capital': item.get("capitalLabel", {}).get("value", ""),
                        'poblacion': self._parse_int(item.get("poblacion", {}).get("value")),
                        'area': self._parse_float(item.get("area", {}).get("value")),
                        'latitud': latitud,
                        'longitud': longitud,
                        'imagen_url': item.get("imagen", {}).get("value", ""),
                        'bandera_url': bandera_url,
                        'wikidata_id': item.get("provincia", {}).get("value", "").split("/")[-1] if item.get("provincia") else "",
                        'cantones': cantones,
                    }
                )
                
                if not created:
                    # Actualizar campos si no fue creado
                    provincia.capital = item.get("capitalLabel", {}).get("value", "")
                    provincia.poblacion = self._parse_int(item.get("poblacion", {}).get("value"))
                    provincia.area = self._parse_float(item.get("area", {}).get("value"))
                    provincia.latitud = latitud
                    provincia.longitud = longitud
                    provincia.imagen_url = item.get("imagen", {}).get("value", "")
                    provincia.bandera_url = bandera_url
                    provincia.cantones = cantones
                    provincias_to_update.append(provincia)
                
                if created:
                    result["created"] += 1
                else:
                    result["updated"] += 1
                    
            except Exception as e:
                result["errors"].append(f"Error procesando provincia {nombre}: {str(e)}")
        
        # Bulk update para eficiencia
        if provincias_to_update:
            Provincia.objects.bulk_update(
                provincias_to_update,
                ['capital', 'poblacion', 'area', 'latitud', 'longitud', 'imagen_url', 'bandera_url', 'cantones'],
                batch_size=50
            )
        
        process_time = time.time() - process_start
        total_time = time.time() - start_time
        
        logger.info(f"Procesamiento completado en {process_time:.2f}s")
        logger.info(f"Sincronización total: {total_time:.2f}s (vs ~26s anterior)")
        
        # Marcar como sincronizado
        self.mark_synced('provincias')
        
        # Invalidar cache de vistas
        self.default_cache.delete('dashboard_stats')
        
        return result
    
    def _get_provincias_cantones_cached(self) -> Dict[str, List[dict]]:
        """Obtener cantones con cache inteligente"""
        cache_key = 'dbpedia_provincias_cantones'
        results = self.sparql_cache.get(cache_key)
        
        if results is None:
            logger.info("Cache miss - consultando DBpedia para cantones")
            # Usar método original pero con cache
            from .sparql_services import DataSyncService
            original_service = DataSyncService()
            results = original_service.get_provincias_cantones()
            if results:
                self.sparql_cache.set(cache_key, results, 86400)
                logger.info(f"Cached cantones para {len(results)} provincias")
        else:
            logger.info(f"Cache hit - cantones para {len(results)} provincias desde cache")
        
        return results or {}
    
    def _parse_coordinates_optimized(self, coord_str: str) -> tuple:
        """Parser optimizado de coordenadas"""
        if not coord_str or "Point(" not in coord_str:
            return None, None
        
        try:
            coords = coord_str.replace("Point(", "").replace(")", "").split()
            if len(coords) == 2:
                return float(coords[1]), float(coords[0])  # lat, lon
        except (ValueError, IndexError):
            pass
        
        return None, None
    
    def _process_banderas(self, dbpedia_results: List[Dict]) -> Dict[str, str]:
        """Procesar banderas DBpedia de forma optimizada"""
        if not dbpedia_results:
            return {}
        
        flags = {}
        for item in dbpedia_results:
            name = item.get("provinciaLabel", {}).get("value", "")
            flag = item.get("banderaSVG", {}).get("value", "")
            
            if name and flag and flag.startswith('http') and flag.endswith('.svg'):
                # Múltiples formas de indexar para búsqueda eficiente
                flags[name.lower()] = flag
                normalized = self.text_processor.normalize_name(name)
                if normalized:
                    flags[normalized] = flag
        
        return flags
    
    def _get_best_flag_url(self, wikidata_item: Dict, dbpedia_flags: Dict, nombre: str) -> str:
        """Obtener mejor URL de bandera combinando fuentes"""
        # Prioridad: Wikidata -> DBpedia
        wikidata_flag = wikidata_item.get("bandera", {}).get("value", "")
        if wikidata_flag:
            return wikidata_flag
        
        # Buscar en DBpedia con múltiples estrategias
        normalized = self.text_processor.normalize_name(nombre)
        return dbpedia_flags.get(nombre.lower()) or dbpedia_flags.get(normalized, "")
    
    def _get_cantones_for_provincia(self, provincia_cantones: Dict, nombre: str) -> List[Dict]:
        """Asociar cantones con provincia de forma optimizada"""
        if not provincia_cantones:
            return []
        
        normalized = self.text_processor.normalize_name(nombre)
        
        # Buscar por coincidencia exacta primero
        for prov_key, cantones in provincia_cantones.items():
            prov_normalized = self.text_processor.normalize_name(prov_key.split(' Province')[0])
            if prov_normalized == normalized:
                return cantones
        
        return []
    
    def _parse_int(self, value: str) -> Optional[int]:
        """Parser optimizado de enteros"""
        if not value:
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _parse_float(self, value: str) -> Optional[float]:
        """Parser optimizado de flotantes"""
        if not value:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    # Métodos de sincronización para otros tipos (implementación similar)
    def sync_parques_nacionales(self) -> Dict[str, Any]:
        """Sincronización optimizada de parques nacionales"""
        if not self.should_sync('parques'):
            return {"created": 0, "updated": 0, "errors": []}
        
        from .models import ParqueNacional
        
        result = {"created": 0, "updated": 0, "errors": []}
        
        start_time = time.time()
        wikidata_results = self.wikidata.get_parques_nacionales()
        
        if not wikidata_results:
            result["errors"].append("No se pudieron obtener datos de parques desde Wikidata")
            return result
        
        for item in wikidata_results:
            try:
                nombre = item.get("parqueLabel", {}).get("value", "")
                if not nombre:
                    continue
                
                latitud, longitud = self._parse_coordinates_optimized(
                    item.get("coords", {}).get("value", "")
                )
                
                fecha_establecimiento = None
                fecha_str = item.get("establecido", {}).get("value", "")
                if fecha_str:
                    try:
                        from datetime import datetime
                        fecha_establecimiento = datetime.fromisoformat(fecha_str.replace("Z", "+00:00")).date()
                    except ValueError:
                        pass
                
                parque, created = ParqueNacional.objects.update_or_create(
                    nombre=nombre,
                    defaults={
                        'descripcion': item.get("descripcion", {}).get("value", ""),
                        'area': self._parse_float(item.get("area", {}).get("value")),
                        'fecha_establecimiento': fecha_establecimiento,
                        'latitud': latitud,
                        'longitud': longitud,
                        'imagen_url': item.get("imagen", {}).get("value", ""),
                        'wikidata_id': item.get("parque", {}).get("value", "").split("/")[-1] if item.get("parque") else "",
                    }
                )
                
                if created:
                    result["created"] += 1
                else:
                    result["updated"] += 1
                    
            except Exception as e:
                result["errors"].append(f"Error procesando parque {nombre}: {str(e)}")
        
        self.mark_synced('parques')
        sync_time = time.time() - start_time
        logger.info(f"Sincronización parques completada en {sync_time:.2f}s")
        
        return result
    
    def sync_sitios_patrimoniales_enhanced(self) -> Dict[str, Any]:
        """Sincronización mejorada de sitios patrimoniales con datos enriquecidos"""
        if not self.should_sync('sitios'):
            return {"created": 0, "updated": 0, "errors": []}
        
        from .models import SitioPatrimonial
        from .enhanced_heritage_services import EnhancedHeritageProcessor
        
        result = {"created": 0, "updated": 0, "errors": []}
        
        start_time = time.time()
        logger.info("Iniciando sincronización enriquecida de sitios patrimoniales")
        
        try:
            # Usar el nuevo procesador enriquecido
            processor = EnhancedHeritageProcessor()
            enhanced_sites = processor.process_heritage_sites()
            
            logger.info(f"Procesados {len(enhanced_sites)} sitios patrimoniales enriquecidos")
            
            for site_data in enhanced_sites:
                try:
                    wikidata_id = site_data.get('wikidata_id', '')
                    if not wikidata_id:
                        continue
                    
                    # Extraer coordenadas
                    coords = site_data.get('coordenadas', {})
                    latitud = coords.get('latitud') if coords else None
                    longitud = coords.get('longitud') if coords else None
                    
                    # Mapear tipo a choices del modelo
                    categoria = site_data.get('categoria', '').upper()
                    tipo_mapping = {
                        'UNESCO': 'UNESCO',
                        'ARQUEOLOGICO': 'ARQUEOLOGICO', 
                        'HISTORICO': 'HISTORICO',
                        'RELIGIOSO': 'RELIGIOSO',
                        'MUSEO': 'MUSEO',
                        'PATRIMONIAL': 'HISTORICO'  # Fallback
                    }
                    tipo = tipo_mapping.get(categoria, 'HISTORICO')
                    
                    # Parsear fechas
                    fecha_creacion = None
                    if site_data.get('fecha_creacion'):
                        try:
                            from datetime import datetime
                            fecha_creacion = datetime.fromisoformat(site_data['fecha_creacion']).date()
                        except:
                            pass
                    
                    fecha_inicio = None
                    if site_data.get('fecha_inicio'):
                        try:
                            fecha_inicio = datetime.fromisoformat(site_data['fecha_inicio']).date()
                        except:
                            pass
                    
                    # Extraer información UNESCO si existe
                    detalles_unesco = site_data.get('detalles_enriquecidos', {}).get('unesco', {})
                    fecha_inscripcion_unesco = None
                    if detalles_unesco.get('fecha_inscripcion'):
                        try:
                            fecha_inscripcion_unesco = datetime.fromisoformat(detalles_unesco['fecha_inscripcion']).date()
                        except:
                            pass
                    
                    # Crear o actualizar sitio
                    sitio, created = SitioPatrimonial.objects.update_or_create(
                        wikidata_id=wikidata_id,
                        defaults={
                            'nombre': site_data.get('nombre', ''),
                            'tipo': tipo,
                            'subtipo': site_data.get('subtipo', ''),
                            'categoria': site_data.get('categoria', ''),
                            'descripcion': site_data.get('descripcion', ''),
                            
                            # Ubicación
                            'latitud': latitud,
                            'longitud': longitud,
                            'provincia': site_data.get('provincia', ''),
                            'ciudad': site_data.get('ciudad', ''),
                            
                            # Fechas históricas
                            'fecha_creacion': fecha_creacion,
                            'fecha_inicio': fecha_inicio,
                            'fecha_inscripcion_unesco': fecha_inscripcion_unesco,
                            
                            # Información arquitectónica
                            'arquitecto': site_data.get('arquitecto', ''),
                            'estilo_arquitectonico': site_data.get('estilo_arquitectonico', ''),
                            'material': site_data.get('material', ''),
                            
                            # Patrimonio
                            'estatus_patrimonial': site_data.get('estatus_patrimonial', ''),
                            'numero_unesco': detalles_unesco.get('numero_unesco', ''),
                            'criterios_unesco': detalles_unesco.get('criterios', ''),
                            
                            # Medidas físicas
                            'altura': site_data.get('altura'),
                            'area': site_data.get('area'),
                            'superficie': detalles_unesco.get('superficie'),
                            'visitantes_anuales': detalles_unesco.get('visitantes_anuales'),
                            
                            # Información arqueológica si existe
                            'elevacion': site_data.get('detalles_enriquecidos', {}).get('arqueologico', {}).get('elevacion'),
                            'estado_conservacion': site_data.get('detalles_enriquecidos', {}).get('arqueologico', {}).get('estado_conservacion', ''),
                            
                            # Información religiosa si existe
                            'capacidad': site_data.get('detalles_enriquecidos', {}).get('religioso', {}).get('capacidad'),
                            
                            # Enlaces
                            'imagen_url': site_data.get('imagen_url', ''),
                            'website': site_data.get('website', ''),
                            'wikipedia_url': site_data.get('wikipedia_url', ''),
                            'commons_url': site_data.get('commons_url', ''),
                            
                            # Detalles enriquecidos completos
                            'detalles_enriquecidos': site_data.get('detalles_enriquecidos', {})
                        }
                    )
                    
                    if created:
                        result["created"] += 1
                    else:
                        result["updated"] += 1
                        
                except Exception as e:
                    error_msg = f"Error procesando sitio {site_data.get('nombre', 'desconocido')}: {str(e)}"
                    result["errors"].append(error_msg)
                    logger.error(error_msg)
            
            self.mark_synced('sitios')
            sync_time = time.time() - start_time
            logger.info(f"Sincronización sitios enriquecida completada en {sync_time:.2f}s")
            
        except Exception as e:
            error_msg = f"Error general en sincronización de sitios: {str(e)}"
            result["errors"].append(error_msg)
            logger.error(error_msg)
        
        return result
    
    def sync_plazas_optimized(self) -> Dict[str, Any]:
        """Sincronización optimizada de plazas"""
        if not self.should_sync('plazas'):
            return {"created": 0, "updated": 0, "errors": []}
        
        from .models import Plaza
        
        result = {"created": 0, "updated": 0, "errors": []}
        
        start_time = time.time()
        wikidata_results = self.wikidata.get_plazas()
        
        if not wikidata_results:
            result["errors"].append("No se pudieron obtener datos de plazas desde Wikidata")
            return result
        
        for item in wikidata_results:
            try:
                nombre = item.get("plazaLabel", {}).get("value", "")
                if not nombre:
                    continue
                
                # Procesar coordenadas
                latitud, longitud = self._parse_coordinates_optimized(
                    item.get("coordenadas", {}).get("value", "")
                )
                
                plaza_data = {
                    'nombre': nombre,
                    'ciudad': item.get("ciudadLabel", {}).get("value", ""),
                    'provincia': item.get("provinciaLabel", {}).get("value", ""),
                    'descripcion': item.get("descripcion", {}).get("value", ""),
                    'latitud': latitud,
                    'longitud': longitud,
                    'imagen_url': item.get("imagen", {}).get("value", ""),
                    'wikidata_id': item.get("plaza", {}).get("value", "").split('/')[-1] if item.get("plaza") else None,
                }
                
                plaza, created = Plaza.objects.update_or_create(
                    wikidata_id=plaza_data['wikidata_id'],
                    defaults=plaza_data
                )
                
                if created:
                    result["created"] += 1
                else:
                    result["updated"] += 1
                    
            except Exception as e:
                error_msg = f"Error procesando plaza {nombre}: {str(e)}"
                result["errors"].append(error_msg)
                logger.error(error_msg)
        
        # Marcar como sincronizado
        self.mark_synced('plazas')
        
        sync_time = time.time() - start_time
        logger.info(f"Sincronización de plazas completada en {sync_time:.2f}s: {result}")
        
        return result
    
    def sync_all_optimized(self) -> Dict[str, Any]:
        """Sincronización optimizada de todos los datos con rate limiting"""
        start_time = time.time()
        logger.info("Iniciando sincronización optimizada completa")
        
        # Ejecutar sincronizaciones solo si es necesario, con delays
        result = {}
        
        if self.should_sync('provincias'):
            result["provincias"] = self.sync_provincias_concurrent()
            time.sleep(2)  # Delay para evitar rate limiting
        else:
            result["provincias"] = {"created": 0, "updated": 0, "errors": [], "skipped": True}
            
        if self.should_sync('parques'):
            result["parques"] = self.sync_parques_nacionales()
            time.sleep(2)  # Delay para evitar rate limiting
        else:
            result["parques"] = {"created": 0, "updated": 0, "errors": [], "skipped": True}
            
        if self.should_sync('sitios'):
            result["sitios"] = self.sync_sitios_patrimoniales_enhanced()
            time.sleep(2)  # Delay para evitar rate limiting
        else:
            result["sitios"] = {"created": 0, "updated": 0, "errors": [], "skipped": True}
            
        if self.should_sync('plazas'):
            result["plazas"] = self.sync_plazas_optimized()
        else:
            result["plazas"] = {"created": 0, "updated": 0, "errors": [], "skipped": True}
        
        total_time = time.time() - start_time
        logger.info(f"Sincronización completa optimizada en {total_time:.2f}s")
        
        return result