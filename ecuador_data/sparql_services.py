"""
Servicios SPARQL para consultar datos de Wikidata y DBpedia
"""
import logging
from typing import Dict, List, Optional, Any
from SPARQLWrapper import SPARQLWrapper, JSON
from django.conf import settings

logger = logging.getLogger(__name__)

class SPARQLService:
    """Servicio base para consultas SPARQL"""
    
    def __init__(self, endpoint_url: str):
        self.sparql = SPARQLWrapper(endpoint_url)
        self.sparql.setReturnFormat(JSON)
    
    def query(self, query_string: str) -> Optional[List[Dict[str, Any]]]:
        """Ejecuta una consulta SPARQL y retorna los resultados"""
        try:
            self.sparql.setQuery(query_string)
            results = self.sparql.query().convert()
            return results["results"]["bindings"]
        except Exception as e:
            logger.error(f"Error en consulta SPARQL: {e}")
            return None

class WikidataService(SPARQLService):
    """Servicio para consultas a Wikidata"""
    
    def __init__(self):
        super().__init__("https://query.wikidata.org/sparql")
    
    def get_provincias(self) -> Optional[List[Dict[str, Any]]]:
        """Obtiene todas las provincias del Ecuador desde Wikidata"""
        query = """
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX bd: <http://www.bigdata.com/rdf#>
        PREFIX schema: <http://schema.org/>

        SELECT ?item ?itemLabel ?wiki ?population ?area ?capitalLabel ?coord ?lat ?lon ?flag WHERE {
          ?item wdt:P31 wd:Q719987 .  # Instancia de provincia de Ecuador
          OPTIONAL { ?item wdt:P1082 ?population }
          OPTIONAL { ?item wdt:P2046 ?area }
          OPTIONAL { ?item wdt:P36 ?capital }
          OPTIONAL { ?item wdt:P41 ?flag }
          OPTIONAL {
            ?wiki schema:about ?item ;
                  schema:isPartOf <https://es.wikipedia.org/> .
          }
          SERVICE wikibase:label { bd:serviceParam wikibase:language "es" }
          OPTIONAL { ?item wdt:P625 ?coord .
            BIND(geof:latitude(?coord) AS ?lat)
            BIND(geof:longitude(?coord) AS ?lon)
          }
        }
        ORDER BY ?itemLabel
        """
        return self.query(query)
    
    def get_provincias_detalladas(self) -> Optional[List[Dict[str, Any]]]:
        """Obtiene provincias con información detallada incluyendo imágenes"""
        query = """
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX bd: <http://www.bigdata.com/rdf#>
        PREFIX schema: <http://schema.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?provincia ?provinciaLabel ?capitalLabel ?poblacion ?area ?coordenadas ?imagen ?bandera WHERE {
          VALUES ?provincia {
            wd:Q220451 wd:Q261165 wd:Q321729 wd:Q335471 wd:Q238492 wd:Q241140 
            wd:Q466019 wd:Q335526 wd:Q335464 wd:Q321863 wd:Q504238 wd:Q504260 
            wd:Q504666 wd:Q549522 wd:Q211900 wd:Q499475 wd:Q214814 wd:Q272586 
            wd:Q475038 wd:Q504252 wd:Q1124125 wd:Q1123208 wd:Q499456 wd:Q744670
          }
          
          OPTIONAL { ?provincia wdt:P36 ?capital }
          OPTIONAL { ?provincia wdt:P1082 ?poblacion }
          OPTIONAL { ?provincia wdt:P2046 ?area }
          OPTIONAL { ?provincia wdt:P625 ?coordenadas }
          OPTIONAL { ?provincia wdt:P18 ?imagen }
          OPTIONAL { ?provincia wdt:P41 ?bandera }

          SERVICE wikibase:label { 
            bd:serviceParam wikibase:language "[AUTO_LANGUAGE],es,en" . 
          }
        }
        ORDER BY ?provinciaLabel
        """
        return self.query(query)
    
    def get_parques_nacionales(self) -> Optional[List[Dict[str, Any]]]:
        """Obtiene parques nacionales del Ecuador desde Wikidata"""
        query = """
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX bd: <http://www.bigdata.com/rdf#>

        SELECT DISTINCT ?parque ?parqueLabel ?coords ?imagen ?descripcion ?area ?establecido ?provincia WHERE {
          ?parque (wdt:P31/wdt:P279*) wd:Q46169 .  # Parques nacionales
          ?parque wdt:P17 wd:Q736 .                 # En Ecuador
          
          OPTIONAL { ?parque wdt:P625 ?coords }     # Coordenadas
          OPTIONAL { ?parque wdt:P18 ?imagen }      # Imagen
          OPTIONAL { ?parque wdt:P2046 ?area }      # Área en km²
          OPTIONAL { ?parque wdt:P571 ?establecido } # Fecha de establecimiento
          OPTIONAL { ?parque wdt:P131 ?provincia }  # División administrativa (provincia)
          OPTIONAL { ?parque wdt:P856 ?website }    # Sitio web oficial
          
          SERVICE wikibase:label {
            bd:serviceParam wikibase:language "es,en" .
          }
        }
        ORDER BY ?parqueLabel
        """
        return self.query(query)
    
    def get_sitios_patrimoniales(self) -> Optional[List[Dict[str, Any]]]:
        """Obtiene sitios patrimoniales del Ecuador desde Wikidata"""
        query = """
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX bd: <http://www.bigdata.com/rdf#>

        SELECT ?sitio ?sitioLabel ?tipo ?tipoLabel ?coords ?imagen ?descripcion WHERE {
          ?sitio wdt:P17 wd:Q736 .                  # En Ecuador
          {
            ?sitio wdt:P1435 wd:Q9259 .             # Patrimonio Mundial UNESCO
          } UNION {
            ?sitio (wdt:P31/wdt:P279*) wd:Q839954 . # Sitios arqueológicos
          } UNION {
            ?sitio (wdt:P31/wdt:P279*) wd:Q32815 .  # Centros históricos
          }
          OPTIONAL { ?sitio wdt:P31 ?tipo }
          OPTIONAL { ?sitio wdt:P625 ?coords }
          OPTIONAL { ?sitio wdt:P18 ?imagen }
          
          SERVICE wikibase:label { 
            bd:serviceParam wikibase:language "es". 
          }
        }
        """
        return self.query(query)
    
    def get_plazas(self) -> Optional[List[Dict[str, Any]]]:
        """Obtiene plazas del Ecuador desde Wikidata"""
        query = """
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX bd: <http://www.bigdata.com/rdf#>

        SELECT ?plaza ?plazaLabel ?ciudad ?ciudadLabel ?coords ?imagen WHERE {
          ?plaza (wdt:P31/wdt:P279*) wd:Q174782 .   # Plazas
          ?plaza wdt:P17 wd:Q736 .                  # En Ecuador
          OPTIONAL { ?plaza wdt:P131 ?ciudad }      # Ciudad
          OPTIONAL { ?plaza wdt:P625 ?coords }      # Coordenadas
          OPTIONAL { ?plaza wdt:P18 ?imagen }       # Imagen
          
          SERVICE wikibase:label { 
            bd:serviceParam wikibase:language "es,en" . 
          }
        }
        LIMIT 100
        """
        return self.query(query)

class DBpediaService(SPARQLService):
    """Servicio para consultas a DBpedia"""
    
    def __init__(self):
        super().__init__("http://dbpedia.org/sparql")
    
    def get_provincias_banderas(self) -> Optional[List[Dict[str, Any]]]:
        """Obtiene banderas de las provincias del Ecuador desde DBpedia"""
        query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>

        SELECT ?provincia ?provinciaLabel (SAMPLE(?svg) AS ?banderaSVG)
        WHERE {
          VALUES ?provincia {
            <http://dbpedia.org/resource/Azuay_Province>
            <http://dbpedia.org/resource/Bolívar_Province,_Ecuador>
            <http://dbpedia.org/resource/Cañar_Province>
            <http://dbpedia.org/resource/Carchi_Province>
            <http://dbpedia.org/resource/Chimborazo_Province>
            <http://dbpedia.org/resource/Cotopaxi_Province>
            <http://dbpedia.org/resource/El_Oro_Province>
            <http://dbpedia.org/resource/Esmeraldas_Province>
            <http://dbpedia.org/resource/Galápagos_Province>
            <http://dbpedia.org/resource/Guayas_Province>
            <http://dbpedia.org/resource/Imbabura_Province>
            <http://dbpedia.org/resource/Loja_Province>
            <http://dbpedia.org/resource/Los_Ríos_Province>
            <http://dbpedia.org/resource/Manabí_Province>
            <http://dbpedia.org/resource/Morona_Santiago_Province>
            <http://dbpedia.org/resource/Napo_Province>
            <http://dbpedia.org/resource/Orellana_Province>
            <http://dbpedia.org/resource/Pastaza_Province>
            <http://dbpedia.org/resource/Pichincha_Province>
            <http://dbpedia.org/resource/Santa_Elena_Province>
            <http://dbpedia.org/resource/Santo_Domingo_de_los_Tsáchilas_Province>
            <http://dbpedia.org/resource/Sucumbíos_Province>
            <http://dbpedia.org/resource/Tungurahua_Province>
            <http://dbpedia.org/resource/Zamora-Chinchipe_Province>
          }

          ?provincia rdfs:label ?provinciaLabel .
          FILTER(LANG(?provinciaLabel) = "es")

          OPTIONAL {
            ?provincia foaf:depiction ?svg .
            FILTER(CONTAINS(LCASE(STR(?svg)), ".svg"))
          }
        }
        GROUP BY ?provincia ?provinciaLabel
        ORDER BY ?provinciaLabel
        """
        return self.query(query)
    
    def get_provincias_info(self) -> Optional[List[Dict[str, Any]]]:
        """Obtiene información básica de provincias desde DBpedia"""
        query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT DISTINCT ?provincia ?nombre ?capital WHERE {
          ?provincia rdf:type dbo:AdministrativeRegion ;
                     dbo:country dbr:Ecuador ;
                     rdfs:label ?nombre .
          OPTIONAL { ?provincia dbo:capital ?capital }
          FILTER(langMatches(lang(?nombre), "en"))
          FILTER(CONTAINS(LCASE(STR(?provincia)), "province"))
        }
        ORDER BY ?nombre
        """
        return self.query(query)

class DataSyncService:
    """Servicio para sincronizar datos desde SPARQL a la base de datos Django"""
    
    def __init__(self):
        self.wikidata = WikidataService()
        self.dbpedia = DBpediaService()
    
    def get_provincias_cantones(self) -> Dict[str, List[dict]]:
        """Obtiene subdivisiones (cantones) de cada provincia desde DBpedia, con propiedades relevantes y sin repeticiones"""
        query = '''
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX dbp: <http://dbpedia.org/property/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX schema: <http://schema.org/>

        SELECT DISTINCT ?provincia ?provinciaName ?subdivision ?subdivisionName ?cantonUrl ?desc ?cabecera ?poblacion ?lat ?long WHERE {
          {
            ?provincia dbo:country dbr:Ecuador ;
                       dbo:subdivision ?subdivision .
            FILTER(CONTAINS(STR(?provincia), "Province"))
          } UNION {
            ?subdivision dbo:subdivision ?provincia .
            ?provincia dbo:country dbr:Ecuador .
            FILTER(CONTAINS(STR(?provincia), "Province"))
          } UNION {
            ?subdivision dbp:subdivisionName ?provincia .
            ?provincia dbo:country dbr:Ecuador .
            FILTER(CONTAINS(STR(?provincia), "Province"))
          }
          OPTIONAL { ?provincia rdfs:label ?provinciaName . FILTER(LANG(?provinciaName) = "en") }
          OPTIONAL { ?subdivision rdfs:label ?subdivisionName . FILTER(LANG(?subdivisionName) = "en") }
          OPTIONAL { ?subdivision foaf:isPrimaryTopicOf ?cantonUrl }
          OPTIONAL { ?subdivision dbo:abstract ?desc . FILTER(LANG(?desc) = "es") }
          OPTIONAL { ?subdivision dbp:seat ?cabecera }
          OPTIONAL { ?subdivision dbp:populationTotal ?poblacion }
          OPTIONAL { ?subdivision geo:lat ?lat }
          OPTIONAL { ?subdivision geo:long ?long }
        }
        ORDER BY ?provincia ?subdivision
        '''
        results = self.dbpedia.query(query)
        provincia_cantones = {}
        import re
        for item in results or []:
            prov_label = item.get("provinciaName", {}).get("value", "")
            canton_label = item.get("subdivisionName", {}).get("value", "")
            if prov_label and canton_label:
                match = re.search(r"^(.*?)\s*P(?:rovince|rovincia)$", prov_label)
                if match:
                    key = match.group(1).strip()
                else:
                    key = prov_label.strip()
                # Construir diccionario de propiedades relevantes
                canton_dict = {
                    "nombre": canton_label.strip(),
                    "url": item.get("cantonUrl", {}).get("value", ""),
                    "descripcion": item.get("desc", {}).get("value", ""),
                    "cabecera": item.get("cabecera", {}).get("value", ""),
                    "poblacion": item.get("poblacion", {}).get("value", ""),
                    "latitud": item.get("lat", {}).get("value", ""),
                    "longitud": item.get("long", {}).get("value", ""),
                }
                # Evitar cantones repetidos por nombre
                if key not in provincia_cantones:
                    provincia_cantones[key] = []
                nombres_existentes = [c["nombre"] for c in provincia_cantones[key]]
                if canton_dict["nombre"] not in nombres_existentes:
                    provincia_cantones[key].append(canton_dict)
        return provincia_cantones

    def sync_provincias(self) -> Dict[str, Any]:
        """Sincroniza datos de provincias desde Wikidata y DBpedia"""
        from .models import Provincia

        result = {
            "created": 0,
            "updated": 0,
            "errors": []
        }

        # Obtener datos de Wikidata
        wikidata_results = self.wikidata.get_provincias_detalladas()
        if not wikidata_results:
            result["errors"].append("No se pudieron obtener datos de Wikidata")
            return result

        # Obtener banderas de DBpedia
        dbpedia_flags = {}
        dbpedia_results = self.dbpedia.get_provincias_banderas()
        if dbpedia_results:
            for item in dbpedia_results:
                name = item.get("provinciaLabel", {}).get("value", "")
                flag = item.get("banderaSVG", {}).get("value", "")
                # Validar que el enlace sea SVG y público
                if name and flag and flag.startswith('http') and flag.endswith('.svg'):
                    dbpedia_flags[name.lower()] = flag
                # También guardar por label sin tildes ni paréntesis
                import unicodedata
                def limpiar_label(label):
                    label = unicodedata.normalize('NFKD', label).encode('ASCII', 'ignore').decode('ASCII')
                    label = label.lower().replace('(','').replace(')','').replace('provincia','').replace('ecuador','').replace('islas','').replace('del','').replace('de','').replace('la','').replace('el','').replace('los','').replace('las','').replace(' ','').strip()
                    return label
                dbpedia_flags[limpiar_label(name)] = flag

        # Obtener cantones de DBpedia
        provincia_cantones = self.get_provincias_cantones()

        for item in wikidata_results:
            try:
                nombre = item.get("provinciaLabel", {}).get("value", "")
                if not nombre:
                    continue

                # Extraer coordenadas
                latitud = None
                longitud = None
                coord_str = item.get("coordenadas", {}).get("value", "")
                if coord_str:
                    # Formato: Point(longitude latitude)
                    if "Point(" in coord_str:
                        coords = coord_str.replace("Point(", "").replace(")", "").split()
                        if len(coords) == 2:
                            try:
                                longitud = float(coords[0])
                                latitud = float(coords[1])
                            except ValueError:
                                pass

                # Bandera: primero Wikidata, si no hay, usar DBpedia
                # Buscar bandera en Wikidata (P41) y DBpedia (SVG)
                bandera_wikidata = item.get("bandera", {}).get("value", "") if "bandera" in item else ""
                import unicodedata
                def normaliza_nombre(n):
                    n = unicodedata.normalize('NFKD', n).encode('ASCII', 'ignore').decode('ASCII')
                    n = n.lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
                    n = n.replace('ñ','n').replace('ü','u')
                    n = n.replace('provincia','').replace('province','').replace(',','').replace('_',' ').replace('-',' ')
                    n = n.replace('  ',' ').strip()
                    return n
                bandera_dbpedia = dbpedia_flags.get(normaliza_nombre(nombre), "")
                if not bandera_dbpedia:
                    nombre_limpio = limpiar_label(nombre)
                    bandera_dbpedia = dbpedia_flags.get(nombre_limpio, "")
                if not bandera_dbpedia:
                    for k in dbpedia_flags:
                        if nombre.lower() in k or k in nombre.lower() or nombre_limpio in k or k in nombre_limpio:
                            bandera_dbpedia = dbpedia_flags[k]
                            break
                if not bandera_wikidata and bandera_dbpedia and bandera_dbpedia.endswith('.svg'):
                    bandera_url = bandera_dbpedia
                elif bandera_wikidata:
                    bandera_url = bandera_wikidata
                else:
                    bandera_url = ''

                # Asociar cantones por nombre: compara con el texto antes de ' Province'
                import unicodedata
                def limpiar_nombre(n):
                    n = unicodedata.normalize('NFKD', n).encode('ASCII', 'ignore').decode('ASCII')
                    n = n.lower().replace('provincia','').replace('province','').replace('ecuador','').replace('del','').replace('de','').replace('la','').replace('el','').replace('los','').replace('las','').replace('islas','').replace('-','').replace('_','').replace(',','').replace('(','').replace(')','').replace('  ',' ').replace(' ','').strip()
                    return n
                cantones = []
                nombre_es = limpiar_nombre(nombre)
                for prov_en, lista_cantones in provincia_cantones.items():
                    base_en = limpiar_nombre(prov_en.split(' Province')[0])
                    if base_en == nombre_es:
                        cantones = lista_cantones
                        break
                provincia, created = Provincia.objects.update_or_create(
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

                if created:
                    result["created"] += 1
                else:
                    result["updated"] += 1

            except Exception as e:
                result["errors"].append(f"Error procesando provincia {nombre}: {str(e)}")
        return result
    
    def sync_parques_nacionales(self) -> Dict[str, Any]:
        """Sincroniza datos de parques nacionales desde Wikidata"""
        from .models import ParqueNacional
        
        result = {
            "created": 0,
            "updated": 0,
            "errors": []
        }
        
        wikidata_results = self.wikidata.get_parques_nacionales()
        if not wikidata_results:
            result["errors"].append("No se pudieron obtener datos de parques desde Wikidata")
            return result
        
        for item in wikidata_results:
            try:
                nombre = item.get("parqueLabel", {}).get("value", "")
                if not nombre:
                    continue
                
                # Extraer coordenadas
                latitud = None
                longitud = None
                coord_str = item.get("coords", {}).get("value", "")
                if coord_str:
                    if "Point(" in coord_str:
                        coords = coord_str.replace("Point(", "").replace(")", "").split()
                        if len(coords) == 2:
                            try:
                                longitud = float(coords[0])
                                latitud = float(coords[1])
                            except ValueError:
                                pass
                
                # Procesar fecha de establecimiento
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
        
        return result
    
    def sync_sitios_patrimoniales(self) -> Dict[str, Any]:
        """Sincroniza datos de sitios patrimoniales desde Wikidata"""
        from .models import SitioPatrimonial
        
        result = {
            "created": 0,
            "updated": 0,
            "errors": []
        }
        
        wikidata_results = self.wikidata.get_sitios_patrimoniales()
        if not wikidata_results:
            result["errors"].append("No se pudieron obtener datos de sitios desde Wikidata")
            return result
        
        for item in wikidata_results:
            try:
                nombre = item.get("sitioLabel", {}).get("value", "")
                if not nombre:
                    continue
                
                # Extraer coordenadas
                latitud = None
                longitud = None
                coord_str = item.get("coords", {}).get("value", "")
                if coord_str:
                    if "Point(" in coord_str:
                        coords = coord_str.replace("Point(", "").replace(")", "").split()
                        if len(coords) == 2:
                            try:
                                longitud = float(coords[0])
                                latitud = float(coords[1])
                            except ValueError:
                                pass
                
                sitio, created = SitioPatrimonial.objects.update_or_create(
                    nombre=nombre,
                    defaults={
                        'tipo': item.get("tipoLabel", {}).get("value", ""),
                        'descripcion': item.get("descripcion", {}).get("value", ""),
                        'latitud': latitud,
                        'longitud': longitud,
                        'imagen_url': item.get("imagen", {}).get("value", ""),
                        'wikidata_id': item.get("sitio", {}).get("value", "").split("/")[-1] if item.get("sitio") else "",
                    }
                )
                
                if created:
                    result["created"] += 1
                else:
                    result["updated"] += 1
                    
            except Exception as e:
                result["errors"].append(f"Error procesando sitio {nombre}: {str(e)}")
        
        return result
    
    def sync_plazas(self) -> Dict[str, Any]:
        """Sincroniza datos de plazas desde Wikidata"""
        from .models import Plaza
        
        result = {
            "created": 0,
            "updated": 0,
            "errors": []
        }
        
        wikidata_results = self.wikidata.get_plazas()
        if not wikidata_results:
            result["errors"].append("No se pudieron obtener datos de plazas desde Wikidata")
            return result
        
        for item in wikidata_results:
            try:
                nombre = item.get("plazaLabel", {}).get("value", "")
                if not nombre:
                    continue
                
                # Extraer coordenadas
                latitud = None
                longitud = None
                coord_str = item.get("coords", {}).get("value", "")
                if coord_str:
                    if "Point(" in coord_str:
                        coords = coord_str.replace("Point(", "").replace(")", "").split()
                        if len(coords) == 2:
                            try:
                                longitud = float(coords[0])
                                latitud = float(coords[1])
                            except ValueError:
                                pass
                
                plaza, created = Plaza.objects.update_or_create(
                    nombre=nombre,
                    defaults={
                        'ciudad': item.get("ciudadLabel", {}).get("value", ""),
                        'descripcion': "",  # No disponible en la consulta base
                        'latitud': latitud,
                        'longitud': longitud,
                        'imagen_url': item.get("imagen", {}).get("value", ""),
                        'wikidata_id': item.get("plaza", {}).get("value", "").split("/")[-1] if item.get("plaza") else "",
                    }
                )
                
                if created:
                    result["created"] += 1
                else:
                    result["updated"] += 1
                    
            except Exception as e:
                result["errors"].append(f"Error procesando plaza {nombre}: {str(e)}")
        
        return result
    
    def sync_all(self) -> Dict[str, Any]:
        """Sincroniza todos los datos"""
        result = {
            "provincias": self.sync_provincias(),
            "parques": self.sync_parques_nacionales(),
            "sitios": self.sync_sitios_patrimoniales(),
            "plazas": self.sync_plazas(),
        }
        return result
    
    def _parse_int(self, value: str) -> Optional[int]:
        """Convierte string a entero de forma segura"""
        if not value:
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _parse_float(self, value: str) -> Optional[float]:
        """Convierte string a float de forma segura"""
        if not value:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
