"""
Servicios SPARQL mejorados para Sitios Patrimoniales de Ecuador
Utiliza múltiples fuentes LOD para información enriquecida
"""
import logging
from typing import Dict, List, Optional, Any
from SPARQLWrapper import SPARQLWrapper, JSON
from .sparql_services import SPARQLService

logger = logging.getLogger(__name__)

class EnhancedHeritageService:
    """Servicio mejorado para sitios patrimoniales con múltiples fuentes LOD"""
    
    def __init__(self):
        self.wikidata = SPARQLService("https://query.wikidata.org/sparql")
        self.dbpedia = SPARQLService("http://dbpedia.org/sparql")

    
    def get_enhanced_heritage_sites(self) -> Optional[List[Dict[str, Any]]]:
        """
        Consulta mejorada para sitios patrimoniales de Ecuador con información enriquecida
        Incluye: UNESCO, arqueológicos, históricos, iglesias, museos, monumentos
        """
        query = """
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX bd: <http://www.bigdata.com/rdf#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <http://schema.org/>

        SELECT DISTINCT ?sitio ?sitioLabel ?sitioDescription 
               ?tipo ?tipoLabel ?subtipo ?subtipoLabel
               ?coords ?imagen ?website
               ?fechaCreacion ?fechaInicio ?fechaFin
               ?arquitecto ?arquitectoLabel
               ?estilo ?estiloLabel
               ?material ?materialLabel
               ?patrimonio ?patrimonioLabel
               ?provincia ?provinciaLabel
               ?ciudad ?ciudadLabel
               ?altura ?area 
               ?wikipedia ?commons
        WHERE {
          ?sitio wdt:P17 wd:Q736 .  # País: Ecuador
          
          {
            # Patrimonio Mundial UNESCO
            ?sitio wdt:P1435 wd:Q9259 .
            BIND("UNESCO" as ?categoria)
          } UNION {
            # Sitios arqueológicos
            ?sitio (wdt:P31/wdt:P279*) wd:Q839954 .
            BIND("Arqueológico" as ?categoria)
          } UNION {
            # Centros históricos
            ?sitio (wdt:P31/wdt:P279*) wd:Q32815 .
            BIND("Centro Histórico" as ?categoria)
          } UNION {
            # Iglesias y catedrales
            ?sitio (wdt:P31/wdt:P279*) wd:Q16970 .
            BIND("Religioso" as ?categoria)
          } UNION {
            # Museos
            ?sitio (wdt:P31/wdt:P279*) wd:Q33506 .
            BIND("Museo" as ?categoria)
          } UNION {
            # Monumentos
            ?sitio (wdt:P31/wdt:P279*) wd:Q4989906 .
            BIND("Monumento" as ?categoria)
          } UNION {
            # Fortalezas y fortificaciones
            ?sitio (wdt:P31/wdt:P279*) wd:Q1785071 .
            BIND("Fortificación" as ?categoria)
          } UNION {
            # Palacios
            ?sitio (wdt:P31/wdt:P279*) wd:Q16560 .
            BIND("Palacio" as ?categoria)
          } UNION {
            # Bibliotecas históricas
            ?sitio (wdt:P31/wdt:P279*) wd:Q7075 .
            BIND("Biblioteca" as ?categoria)
          } UNION {
            # Teatros históricos
            ?sitio (wdt:P31/wdt:P279*) wd:Q24354 .
            BIND("Teatro" as ?categoria)
          } UNION {
            # Mercados tradicionales
            ?sitio (wdt:P31/wdt:P279*) wd:Q37654 .
            BIND("Mercado" as ?categoria)
          }
          
          # Información básica
          ?sitio wdt:P31 ?tipo .
          OPTIONAL { ?sitio wdt:P279 ?subtipo }
          OPTIONAL { ?sitio wdt:P625 ?coords }
          OPTIONAL { ?sitio wdt:P18 ?imagen }
          OPTIONAL { ?sitio wdt:P856 ?website }
          
          # Fechas históricas
          OPTIONAL { ?sitio wdt:P571 ?fechaCreacion }  # Fecha de creación
          OPTIONAL { ?sitio wdt:P580 ?fechaInicio }    # Fecha de inicio
          OPTIONAL { ?sitio wdt:P582 ?fechaFin }       # Fecha de fin
          
          # Información arquitectónica
          OPTIONAL { ?sitio wdt:P84 ?arquitecto }      # Arquitecto
          OPTIONAL { ?sitio wdt:P149 ?estilo }         # Estilo arquitectónico
          OPTIONAL { ?sitio wdt:P186 ?material }       # Material
          
          # Clasificación patrimonial
          OPTIONAL { ?sitio wdt:P1435 ?patrimonio }    # Estatus patrimonial
          
          # Ubicación detallada
          OPTIONAL { ?sitio wdt:P131 ?ciudad }         # División administrativa
          OPTIONAL { ?ciudad wdt:P131 ?provincia }     # Provincia
          
          # Medidas físicas
          OPTIONAL { ?sitio wdt:P2048 ?altura }        # Altura
          OPTIONAL { ?sitio wdt:P2046 ?area }          # Área
          
          # Enlaces externos
          OPTIONAL {
            ?wikipedia schema:about ?sitio ;
                      schema:isPartOf <https://es.wikipedia.org/> .
          }
          OPTIONAL {
            ?commons schema:about ?sitio ;
                    schema:isPartOf <https://commons.wikimedia.org/> .
          }
          
          # Filtros de calidad
          FILTER(EXISTS { ?sitio rdfs:label ?label . FILTER(lang(?label) = "es") })
          
          SERVICE wikibase:label { 
            bd:serviceParam wikibase:language "es,en" . 
          }
        }
        ORDER BY ?sitioLabel
        """
        return self.wikidata.query(query)
    
    def get_heritage_sites_with_dbpedia_enrichment(self) -> Optional[List[Dict[str, Any]]]:
        """
        Consulta DBpedia para información complementaria sobre sitios ecuatorianos
        """
        query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
        PREFIX dbp: <http://dbpedia.org/property/>
        
        SELECT DISTINCT ?sitio ?nombre ?abstract ?thumbnail ?website
               ?establecido ?estilo ?arquitecto ?tipo
               ?lat ?long ?elevation ?visitantes
               ?imagen ?commons
        WHERE {
          {
            ?sitio dbo:country dbr:Ecuador ;
                   rdf:type dbo:HistoricPlace .
          } UNION {
            ?sitio dbo:country dbr:Ecuador ;
                   rdf:type dbo:Museum .
          } UNION {
            ?sitio dbo:country dbr:Ecuador ;
                   rdf:type dbo:ReligiousBuilding .
          } UNION {
            ?sitio dbo:country dbr:Ecuador ;
                   rdf:type dbo:Monument .
          } UNION {
            ?sitio dbo:location ?location .
            ?location dbo:country dbr:Ecuador .
            ?sitio rdf:type dbo:WorldHeritageSite .
          }
          
          ?sitio rdfs:label ?nombre .
          FILTER(lang(?nombre) = "es" || lang(?nombre) = "en")
          
          OPTIONAL { ?sitio dbo:abstract ?abstract . FILTER(lang(?abstract) = "es") }
          OPTIONAL { ?sitio dbo:thumbnail ?thumbnail }
          OPTIONAL { ?sitio foaf:homepage ?website }
          OPTIONAL { ?sitio dbp:established ?establecido }
          OPTIONAL { ?sitio dbp:architecturalStyle ?estilo }
          OPTIONAL { ?sitio dbp:architect ?arquitecto }
          OPTIONAL { ?sitio rdf:type ?tipo }
          OPTIONAL { ?sitio geo:lat ?lat }
          OPTIONAL { ?sitio geo:long ?long }
          OPTIONAL { ?sitio dbo:elevation ?elevation }
          OPTIONAL { ?sitio dbo:visitorsPerYear ?visitantes }
          OPTIONAL { ?sitio foaf:depiction ?imagen }
          OPTIONAL { ?sitio dbp:commons ?commons }
        }
        ORDER BY ?nombre
        """
        return self.dbpedia.query(query)
    
    def get_unesco_sites_detailed(self) -> Optional[List[Dict[str, Any]]]:
        """
        Consulta específica para sitios UNESCO de Ecuador con máximo detalle
        """
        query = """
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX bd: <http://www.bigdata.com/rdf#>
        PREFIX p: <http://www.wikidata.org/prop/>
        PREFIX ps: <http://www.wikidata.org/prop/statement/>
        PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
        
        SELECT DISTINCT ?sitio ?sitioLabel ?sitioDescription
               ?coords ?imagen ?website ?commons
               ?fechaInscripcion ?criterios ?zona
               ?amenazas ?superficie ?bufferZone
               ?numeroUNESCO ?region ?subregion
               ?provincia ?provinciaLabel
               ?visitantesAnuales ?administrador
        WHERE {
          ?sitio wdt:P17 wd:Q736 ;              # País: Ecuador
                 wdt:P1435 wd:Q9259 .          # Patrimonio Mundial UNESCO
          
          OPTIONAL { ?sitio wdt:P625 ?coords }
          OPTIONAL { ?sitio wdt:P18 ?imagen }
          OPTIONAL { ?sitio wdt:P856 ?website }
          OPTIONAL { ?sitio wdt:P373 ?commons }
          
          # Información específica UNESCO
          OPTIONAL { 
            ?sitio p:P1435 ?patrimonioStatement .
            ?patrimonioStatement ps:P1435 wd:Q9259 .
            OPTIONAL { ?patrimonioStatement pq:P585 ?fechaInscripcion }
            OPTIONAL { ?patrimonioStatement pq:P1013 ?criterios }
          }
          
          OPTIONAL { ?sitio wdt:P2046 ?superficie }      # Superficie
          OPTIONAL { ?sitio wdt:P3134 ?numeroUNESCO }    # Número UNESCO
          OPTIONAL { ?sitio wdt:P131 ?provincia }        # Provincia
          OPTIONAL { ?sitio wdt:P1174 ?visitantesAnuales } # Visitantes por año
          OPTIONAL { ?sitio wdt:P137 ?administrador }    # Operador/administrador
          
          SERVICE wikibase:label { 
            bd:serviceParam wikibase:language "es,en" . 
          }
        }
        ORDER BY ?sitioLabel
        """
        return self.wikidata.query(query)
    
    def get_archaeological_sites_detailed(self) -> Optional[List[Dict[str, Any]]]:
        """
        Consulta detallada para sitios arqueológicos ecuatorianos
        """
        query = """
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX bd: <http://www.bigdata.com/rdf#>
        
        SELECT DISTINCT ?sitio ?sitioLabel ?sitioDescription
               ?coords ?imagen ?elevacion
               ?cultura ?culturaLabel ?periodo ?periodoLabel
               ?fechaDescubrimiento ?descubridor ?descubridorLabel
               ?tipoSitio ?tipoSitioLabel
               ?provincia ?provinciaLabel ?canton ?cantonLabel
               ?superficie ?estado ?estadoLabel
               ?importancia ?importanciaLabel
        WHERE {
          ?sitio wdt:P17 wd:Q736 .                    # País: Ecuador
          ?sitio (wdt:P31/wdt:P279*) wd:Q839954 .     # Sitio arqueológico
          
          OPTIONAL { ?sitio wdt:P625 ?coords }
          OPTIONAL { ?sitio wdt:P18 ?imagen }
          OPTIONAL { ?sitio wdt:P2044 ?elevacion }
          
          # Información arqueológica específica
          OPTIONAL { ?sitio wdt:P2596 ?cultura }       # Cultura
          OPTIONAL { ?sitio wdt:P2348 ?periodo }       # Período temporal
          OPTIONAL { ?sitio wdt:P575 ?fechaDescubrimiento } # Fecha descubrimiento
          OPTIONAL { ?sitio wdt:P61 ?descubridor }     # Descubridor
          OPTIONAL { ?sitio wdt:P31 ?tipoSitio }       # Tipo de sitio
          
          # Ubicación administrativa
          OPTIONAL { ?sitio wdt:P131 ?canton }
          OPTIONAL { ?canton wdt:P131 ?provincia }
          
          # Características físicas
          OPTIONAL { ?sitio wdt:P2046 ?superficie }
          OPTIONAL { ?sitio wdt:P5816 ?estado }        # Estado de conservación
          OPTIONAL { ?sitio wdt:P1435 ?importancia }   # Importancia patrimonial
          
          SERVICE wikibase:label { 
            bd:serviceParam wikibase:language "es,en" . 
          }
        }
        ORDER BY ?sitioLabel
        """
        return self.wikidata.query(query)
    
    def get_religious_heritage_detailed(self) -> Optional[List[Dict[str, Any]]]:
        """
        Consulta detallada para patrimonio religioso ecuatoriano
        """
        query = """
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX bd: <http://www.bigdata.com/rdf#>
        
        SELECT DISTINCT ?sitio ?sitioLabel ?sitioDescription
               ?coords ?imagen ?website
               ?religion ?religionLabel ?denominacion ?denominacionLabel
               ?fechaConstruccion ?arquitecto ?arquitectoLabel
               ?estilo ?estiloLabel ?dedicacion ?dedicacionLabel
               ?diocesis ?diocesisLabel ?parroquia ?parroquiaLabel
               ?provincia ?provinciaLabel ?ciudad ?ciudadLabel
               ?altura ?capacidad ?estado ?estadoLabel
        WHERE {
          ?sitio wdt:P17 wd:Q736 .                    # País: Ecuador
          
          {
            ?sitio (wdt:P31/wdt:P279*) wd:Q16970 .    # Iglesia
          } UNION {
            ?sitio (wdt:P31/wdt:P279*) wd:Q2977 .     # Catedral
          } UNION {
            ?sitio (wdt:P31/wdt:P279*) wd:Q44613 .    # Monasterio
          } UNION {
            ?sitio (wdt:P31/wdt:P279*) wd:Q160742 .   # Abadía
          } UNION {
            ?sitio (wdt:P31/wdt:P279*) wd:Q317557 .   # Basílica
          } UNION {
            ?sitio (wdt:P31/wdt:P279*) wd:Q56242215 . # Santuario
          }
          
          OPTIONAL { ?sitio wdt:P625 ?coords }
          OPTIONAL { ?sitio wdt:P18 ?imagen }
          OPTIONAL { ?sitio wdt:P856 ?website }
          
          # Información religiosa
          OPTIONAL { ?sitio wdt:P140 ?religion }       # Religión
          OPTIONAL { ?sitio wdt:P708 ?diocesis }       # Diócesis
          OPTIONAL { ?sitio wdt:P1259 ?parroquia }     # Parroquia
          OPTIONAL { ?sitio wdt:P825 ?dedicacion }     # Dedicación/Santo patrón
          
          # Información arquitectónica
          OPTIONAL { ?sitio wdt:P571 ?fechaConstruccion }
          OPTIONAL { ?sitio wdt:P84 ?arquitecto }
          OPTIONAL { ?sitio wdt:P149 ?estilo }
          
          # Ubicación
          OPTIONAL { ?sitio wdt:P131 ?ciudad }
          OPTIONAL { ?ciudad wdt:P131 ?provincia }
          
          # Características físicas
          OPTIONAL { ?sitio wdt:P2048 ?altura }
          OPTIONAL { ?sitio wdt:P1083 ?capacidad }
          OPTIONAL { ?sitio wdt:P5816 ?estado }
          
          SERVICE wikibase:label { 
            bd:serviceParam wikibase:language "es,en" . 
          }
        }
        ORDER BY ?sitioLabel
        """
        return self.wikidata.query(query)
    
    def merge_heritage_data(self) -> List[Dict[str, Any]]:
        """
        Combina datos de múltiples fuentes para crear un dataset enriquecido
        """
        logger.info("Iniciando fusión de datos patrimoniales de múltiples fuentes")
        
        # Obtener datos de todas las fuentes
        wikidata_general = self.get_enhanced_heritage_sites() or []
        dbpedia_data = self.get_heritage_sites_with_dbpedia_enrichment() or []
        unesco_detailed = self.get_unesco_sites_detailed() or []
        archaeological_detailed = self.get_archaeological_sites_detailed() or []
        religious_detailed = self.get_religious_heritage_detailed() or []
        
        # Crear índice por nombre para fusión
        merged_sites = {}
        
        # Procesar datos de Wikidata (base principal)
        for site in wikidata_general:
            site_id = site.get('sitio', {}).get('value', '')
            if site_id:
                merged_sites[site_id] = {
                    'source': 'wikidata_general',
                    'data': site,
                    'enrichments': []
                }
        
        # Enriquecer con datos específicos
        for detailed_data, source_name in [
            (unesco_detailed, 'unesco'),
            (archaeological_detailed, 'archaeological'),
            (religious_detailed, 'religious')
        ]:
            for site in detailed_data:
                site_id = site.get('sitio', {}).get('value', '')
                if site_id in merged_sites:
                    merged_sites[site_id]['enrichments'].append({
                        'source': source_name,
                        'data': site
                    })
        
        logger.info(f"Fusión completada: {len(merged_sites)} sitios patrimoniales enriquecidos")
        
        return list(merged_sites.values())


class EnhancedHeritageProcessor:
    """Procesador para limpiar y estructurar datos patrimoniales enriquecidos"""
    
    def __init__(self):
        self.service = EnhancedHeritageService()
    
    def process_heritage_sites(self) -> List[Dict[str, Any]]:
        """
        Procesa y estructura los sitios patrimoniales con información enriquecida
        """
        raw_data = self.service.merge_heritage_data()
        processed_sites = []
        
        for site_data in raw_data:
            base_data = site_data['data']
            enrichments = site_data.get('enrichments', [])
            
            # Extraer información base
            processed_site = {
                'wikidata_id': self._extract_wikidata_id(base_data.get('sitio', {}).get('value', '')),
                'nombre': base_data.get('sitioLabel', {}).get('value', ''),
                'descripcion': base_data.get('sitioDescription', {}).get('value', ''),
                'tipo_principal': base_data.get('tipoLabel', {}).get('value', ''),
                'subtipo': base_data.get('subtipoLabel', {}).get('value', ''),
                'categoria': self._determine_category(base_data),
                
                # Ubicación
                'coordenadas': self._parse_coordinates(base_data.get('coords', {}).get('value', '')),
                'provincia': base_data.get('provinciaLabel', {}).get('value', ''),
                'ciudad': base_data.get('ciudadLabel', {}).get('value', ''),
                
                # Información histórica
                'fecha_creacion': self._parse_date(base_data.get('fechaCreacion', {}).get('value', '')),
                'fecha_inicio': self._parse_date(base_data.get('fechaInicio', {}).get('value', '')),
                'fecha_fin': self._parse_date(base_data.get('fechaFin', {}).get('value', '')),
                
                # Información arquitectónica
                'arquitecto': base_data.get('arquitectoLabel', {}).get('value', ''),
                'estilo_arquitectonico': base_data.get('estiloLabel', {}).get('value', ''),
                'material': base_data.get('materialLabel', {}).get('value', ''),
                
                # Patrimonio
                'estatus_patrimonial': base_data.get('patrimonioLabel', {}).get('value', ''),
                
                # Medidas
                'altura': self._parse_float(base_data.get('altura', {}).get('value', '')),
                'area': self._parse_float(base_data.get('area', {}).get('value', '')),
                
                # Enlaces
                'imagen_url': base_data.get('imagen', {}).get('value', ''),
                'website': base_data.get('website', {}).get('value', ''),
                'wikipedia_url': base_data.get('wikipedia', {}).get('value', ''),
                'commons_url': base_data.get('commons', {}).get('value', ''),
                
                # Información enriquecida
                'detalles_enriquecidos': self._process_enrichments(enrichments)
            }
            
            processed_sites.append(processed_site)
        
        return processed_sites
    
    def _extract_wikidata_id(self, wikidata_url: str) -> str:
        """Extrae el ID de Wikidata de la URL"""
        return wikidata_url.split('/')[-1] if wikidata_url else ''
    
    def _parse_coordinates(self, coord_str: str) -> Dict[str, float]:
        """Parsea coordenadas del formato Point(lon lat)"""
        if not coord_str or "Point(" not in coord_str:
            return {'latitud': None, 'longitud': None}
        
        try:
            coords = coord_str.replace("Point(", "").replace(")", "").split()
            if len(coords) == 2:
                return {
                    'latitud': float(coords[1]),
                    'longitud': float(coords[0])
                }
        except (ValueError, IndexError):
            pass
        
        return {'latitud': None, 'longitud': None}
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parsea fechas ISO a formato legible"""
        if not date_str:
            return None
        
        try:
            # Formato básico para fechas ISO
            if 'T' in date_str:
                return date_str.split('T')[0]
            return date_str[:10] if len(date_str) >= 10 else date_str
        except:
            return date_str
    
    def _parse_float(self, value_str: str) -> Optional[float]:
        """Parsea valores numéricos de forma segura"""
        if not value_str:
            return None
        try:
            return float(value_str)
        except (ValueError, TypeError):
            return None
    
    def _determine_category(self, data: Dict) -> str:
        """Determina la categoría principal del sitio"""
        tipo = data.get('tipoLabel', {}).get('value', '').lower()
        
        if 'unesco' in tipo or 'patrimonio mundial' in tipo:
            return 'UNESCO'
        elif 'arqueológ' in tipo or 'arqueolog' in tipo:
            return 'Arqueológico'
        elif 'iglesia' in tipo or 'catedral' in tipo or 'religios' in tipo:
            return 'Religioso'
        elif 'museo' in tipo:
            return 'Museo'
        elif 'históric' in tipo or 'monument' in tipo:
            return 'Histórico'
        else:
            return 'Patrimonial'
    
    def _process_enrichments(self, enrichments: List[Dict]) -> Dict[str, Any]:
        """Procesa información enriquecida de fuentes específicas"""
        processed = {}
        
        for enrichment in enrichments:
            source = enrichment['source']
            data = enrichment['data']
            
            if source == 'unesco':
                processed['unesco'] = {
                    'fecha_inscripcion': self._parse_date(data.get('fechaInscripcion', {}).get('value', '')),
                    'criterios': data.get('criterios', {}).get('value', ''),
                    'numero_unesco': data.get('numeroUNESCO', {}).get('value', ''),
                    'superficie': self._parse_float(data.get('superficie', {}).get('value', '')),
                    'visitantes_anuales': self._parse_float(data.get('visitantesAnuales', {}).get('value', ''))
                }
            
            elif source == 'archaeological':
                processed['arqueologico'] = {
                    'cultura': data.get('culturaLabel', {}).get('value', ''),
                    'periodo': data.get('periodoLabel', {}).get('value', ''),
                    'fecha_descubrimiento': self._parse_date(data.get('fechaDescubrimiento', {}).get('value', '')),
                    'descubridor': data.get('descubridorLabel', {}).get('value', ''),
                    'elevacion': self._parse_float(data.get('elevacion', {}).get('value', '')),
                    'estado_conservacion': data.get('estadoLabel', {}).get('value', '')
                }
            
            elif source == 'religious':
                processed['religioso'] = {
                    'religion': data.get('religionLabel', {}).get('value', ''),
                    'diocesis': data.get('diocesisLabel', {}).get('value', ''),
                    'dedicacion': data.get('dedicacionLabel', {}).get('value', ''),
                    'capacidad': self._parse_float(data.get('capacidad', {}).get('value', '')),
                    'fecha_construccion': self._parse_date(data.get('fechaConstruccion', {}).get('value', ''))
                }
        
        return processed