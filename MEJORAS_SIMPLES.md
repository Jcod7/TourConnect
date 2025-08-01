# MEJORAS SIMPLES PARA TOURCONNECT

## OBJETIVO GENERAL
Transformar el proyecto actual en una plataforma turística más completa siguiendo la visión del PDF, pero con implementaciones sencillas y prácticas.

## 1. BÚSQUEDA SEMÁNTICA BÁSICA
**Implementación simple:**
- Campo de búsqueda en el header de base.html
- Vista de búsqueda que filtre por nombre en todos los modelos
- Resultados unificados en una sola página

**Código necesario:**
```python
# En views.py
def search_results(request):
    query = request.GET.get('q', '')
    if query:
        sitios = SitioPatrimonial.objects.filter(nombre__icontains=query)
        parques = ParqueNacional.objects.filter(nombre__icontains=query) 
        plazas = Plaza.objects.filter(nombre__icontains=query)
        provincias = Provincia.objects.filter(nombre__icontains=query)
    return render(request, 'search_results.html', {...})
```

## 2. FILTROS MEJORADOS POR TEMÁTICA
**Mejora los filtros existentes:**
- En sitios patrimoniales: agregar filtro por provincia
- En parques: filtrar por tipo de ecosistema
- En plazas: filtrar por importancia histórica

**Sin tocar la base de datos, solo mejorar los templates existentes.**

## 3. INFORMACIÓN TURÍSTICA BÁSICA
**Agregar campos simples a los modelos existentes:**
```python
# En models.py - campos opcionales
class SitioPatrimonial(models.Model):
    # ... campos existentes ...
    horario_visita = models.CharField(max_length=100, blank=True)
    precio_entrada = models.CharField(max_length=50, blank=True)
    servicios_disponibles = models.TextField(blank=True)
    mejor_epoca_visita = models.CharField(max_length=100, blank=True)
```

## 4. RUTAS SUGERIDAS SIMPLES
**Sin algoritmos complejos:**
- Crear modelo básico de rutas predefinidas
- Agrupar sitios por provincia o temática
- Templates que muestren "rutas sugeridas"

```python
class RutaSugerida(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    sitios = models.ManyToManyField(SitioPatrimonial)
    duracion_dias = models.IntegerField()
    tipo = models.CharField(max_length=50)  # cultural, natural, histórica
```

## 5. MEJORAR VISUALIZACIÓN DE UBICACIONES
**Integración simple con mapas:**
- Usar Leaflet (más ligero que Google Maps)
- Mostrar múltiples puntos en un solo mapa
- Vista de mapa general con todos los sitios

## 6. INFORMACIÓN PRÁCTICA
**Templates mejorados con datos útiles:**
- Mostrar distancias entre sitios
- Información de acceso (transporte)
- Enlaces a recursos externos (hoteles, restaurantes cercanos)

## 7. DATOS GUBERNAMENTALES
**Sin complicar la arquitectura:**
- Agregar campos para información oficial
- Enlaces a portales del Ministerio de Turismo
- Información de contacto oficial cuando esté disponible

## PRIORIDADES DE IMPLEMENTACIÓN:

### FASE 1 (1-2 días):
1. Campo de búsqueda global
2. Filtros mejorados en templates existentes
3. Información práctica en detalles

### FASE 2 (2-3 días):
4. Campos turísticos adicionales
5. Rutas sugeridas básicas
6. Mapa integrado simple

### FASE 3 (Futuro):
7. Integración con datos gubernamentales
8. Sistema de valoraciones básico
9. Información de servicios locales

## VENTAJAS DE ESTE ENFOQUE:
- ✅ Mantiene la arquitectura actual
- ✅ Mejoras incrementales
- ✅ No requiere cambios mayores en la base de datos
- ✅ Reutiliza el código SPARQL existente
- ✅ Compatible con el sistema de cache actual
- ✅ Fácil de mantener y extender

## TECNOLOGÍAS ADICIONALES MÍNIMAS:
- Leaflet.js para mapas (CDN, sin instalación)
- Modelos Django adicionales simples
- Templates mejorados con Bootstrap existente
- JavaScript básico para interactividad

Esta aproximación te permitirá alcanzar la visión de TourConnect de manera gradual y sin complicar el proyecto existente.