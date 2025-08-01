from django.contrib import admin
from .models import Provincia, ParqueNacional, SitioPatrimonial, Plaza


@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'capital', 'poblacion', 'area', 'fecha_actualizacion']
    list_filter = ['fecha_actualizacion']
    search_fields = ['nombre', 'capital']
    ordering = ['nombre']
    readonly_fields = ['fecha_actualizacion', 'wikidata_id']


@admin.register(ParqueNacional)
class ParqueNacionalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'area', 'provincia', 'fecha_establecimiento', 'fecha_actualizacion']
    list_filter = ['provincia', 'fecha_actualizacion', 'fecha_establecimiento']
    search_fields = ['nombre', 'provincia']
    ordering = ['nombre']
    readonly_fields = ['fecha_actualizacion', 'wikidata_id']


@admin.register(SitioPatrimonial)
class SitioPatrimonialAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'fecha_actualizacion']
    list_filter = ['tipo', 'fecha_actualizacion']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    readonly_fields = ['fecha_actualizacion', 'wikidata_id']


@admin.register(Plaza)
class PlazaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ciudad', 'fecha_actualizacion']
    list_filter = ['ciudad', 'fecha_actualizacion']
    search_fields = ['nombre', 'ciudad']
    ordering = ['nombre']
    readonly_fields = ['fecha_actualizacion', 'wikidata_id']
