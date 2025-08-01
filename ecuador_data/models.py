from django.db import models
from django.db.models import JSONField

class Provincia(models.Model):
    """Modelo para representar las provincias del Ecuador"""
    nombre = models.CharField(max_length=100)
    capital = models.CharField(max_length=100, blank=True, null=True)
    poblacion = models.IntegerField(blank=True, null=True)
    area = models.FloatField(blank=True, null=True, help_text="Área en km²")
    latitud = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)
    imagen_url = models.URLField(blank=True, null=True)
    bandera_url = models.URLField(blank=True, null=True)
    escudo_url = models.URLField(blank=True, null=True)
    wikipedia_url = models.URLField(blank=True, null=True)
    wikidata_id = models.CharField(max_length=50, unique=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    from django.db.models import JSONField
    cantones = JSONField(blank=True, null=True, default=list)
    
    class Meta:
        verbose_name = "Provincia"
        verbose_name_plural = "Provincias"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class ParqueNacional(models.Model):
    """Modelo para representar los parques nacionales del Ecuador"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    area = models.FloatField(blank=True, null=True, help_text="Área en km²")
    fecha_establecimiento = models.DateField(blank=True, null=True)
    latitud = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)
    imagen_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    wikidata_id = models.CharField(max_length=50, unique=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Parque Nacional"
        verbose_name_plural = "Parques Nacionales"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class SitioPatrimonial(models.Model):
    """Modelo enriquecido para sitios patrimoniales del Ecuador"""
    TIPO_CHOICES = [
        ('UNESCO', 'Patrimonio Mundial UNESCO'),
        ('ARQUEOLOGICO', 'Sitio Arqueológico'),
        ('HISTORICO', 'Centro Histórico'),
        ('RELIGIOSO', 'Patrimonio Religioso'),
        ('MUSEO', 'Museo'),
        ('MONUMENTO', 'Monumento'),
        ('FORTIFICACION', 'Fortificación'),
        ('PALACIO', 'Palacio'),
        ('BIBLIOTECA', 'Biblioteca Histórica'),
        ('TEATRO', 'Teatro Histórico'),
        ('MERCADO', 'Mercado Tradicional'),
    ]
    
    # Información básica
    nombre = models.CharField(max_length=200, db_index=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, db_index=True)
    subtipo = models.CharField(max_length=100, blank=True, null=True)
    categoria = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    descripcion = models.TextField(blank=True, null=True)
    
    # Ubicación
    latitud = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    
    # Información histórica
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    
    # Información arquitectónica
    arquitecto = models.CharField(max_length=200, blank=True, null=True)
    estilo_arquitectonico = models.CharField(max_length=100, blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, null=True)
    
    # Patrimonio y reconocimientos
    estatus_patrimonial = models.CharField(max_length=100, blank=True, null=True)
    numero_unesco = models.CharField(max_length=50, blank=True, null=True)
    fecha_inscripcion_unesco = models.DateField(blank=True, null=True)
    criterios_unesco = models.TextField(blank=True, null=True)
    
    # Medidas físicas (campos con datos)
    # Campos eliminados: altura, area, superficie, elevacion, capacidad (sin datos)
    
    # Enlaces externos
    imagen_url = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    wikipedia_url = models.URLField(blank=True, null=True)
    commons_url = models.URLField(blank=True, null=True)
    
    # Información específica por tipo
    detalles_enriquecidos = JSONField(blank=True, null=True, default=dict)
    
    # Estadísticas
    estado_conservacion = models.CharField(max_length=100, blank=True, null=True)
    
    # Metadatos
    wikidata_id = models.CharField(max_length=50, unique=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Sitio Patrimonial"
        verbose_name_plural = "Sitios Patrimoniales"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['tipo', 'provincia']),
            models.Index(fields=['categoria', 'fecha_inicio']),
            models.Index(fields=['estatus_patrimonial']),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
    
    @property
    def coordenadas(self):
        """Retorna coordenadas como diccionario"""
        if self.latitud and self.longitud:
            return {'latitud': self.latitud, 'longitud': self.longitud}
        return None
    
    @property
    def es_unesco(self):
        """Verifica si es sitio UNESCO"""
        return self.tipo == 'UNESCO' or self.estatus_patrimonial == 'Patrimonio Mundial UNESCO'
    
    @property
    def es_arqueologico(self):
        """Verifica si es sitio arqueológico"""
        return self.tipo == 'ARQUEOLOGICO' or 'arqueológico' in self.descripcion.lower() if self.descripcion else False
    
    @property
    def tiene_fecha_historica(self):
        """Verifica si tiene información de fechas históricas"""
        return any([self.fecha_inicio, self.fecha_inscripcion_unesco])
    
    def get_detalles_por_tipo(self):
        """Retorna detalles específicos según el tipo de sitio"""
        if not self.detalles_enriquecidos:
            return {}
        
        if self.tipo == 'UNESCO':
            return self.detalles_enriquecidos.get('unesco', {})
        elif self.tipo == 'ARQUEOLOGICO':
            return self.detalles_enriquecidos.get('arqueologico', {})
        elif self.tipo == 'RELIGIOSO':
            return self.detalles_enriquecidos.get('religioso', {})
        
        return self.detalles_enriquecidos


class Plaza(models.Model):
    """Modelo para representar las plazas del Ecuador"""
    nombre = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    latitud = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)
    imagen_url = models.URLField(blank=True, null=True)
    wikidata_id = models.CharField(max_length=50, unique=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Plaza"
        verbose_name_plural = "Plazas"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.ciudad}" if self.ciudad else self.nombre
