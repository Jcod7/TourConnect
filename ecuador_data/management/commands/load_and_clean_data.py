"""
Comando para cargar datos desde SPARQL y limpiar datos irrelevantes
"""
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from ecuador_data.models import Provincia, ParqueNacional, SitioPatrimonial, Plaza
from ecuador_data.sparql_services import DataSyncService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Carga datos desde endpoints SPARQL y limpia datos irrelevantes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            choices=['provincias', 'parques', 'sitios', 'plazas', 'all'],
            default='all',
            help='Modelo específico a sincronizar'
        )
        parser.add_argument(
            '--clean-only',
            action='store_true',
            help='Solo limpiar datos, no cargar nuevos'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar carga ignorando cache'
        )

    def handle(self, *args, **options):
        sync_service = DataSyncService()
        
        if not options['clean_only']:
            self.stdout.write(self.style.SUCCESS('Iniciando carga de datos...'))
            
            if options['model'] in ['provincias', 'all']:
                self.sync_provincias(sync_service, options['force'])
            
            if options['model'] in ['parques', 'all']:
                self.sync_parques(sync_service, options['force'])
            
            if options['model'] in ['sitios', 'all']:
                self.sync_sitios(sync_service, options['force'])
            
            if options['model'] in ['plazas', 'all']:
                self.sync_plazas(sync_service, options['force'])
        
        # Limpiar datos irrelevantes
        self.stdout.write(self.style.WARNING('Limpiando datos irrelevantes...'))
        self.clean_irrelevant_data()
        
        self.stdout.write(self.style.SUCCESS('Proceso completado exitosamente.'))

    def sync_provincias(self, sync_service, force=False):
        """Sincronizar provincias"""
        self.stdout.write('Sincronizando provincias...')
        try:
            result = sync_service.sync_provincias()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Provincias sincronizadas: {result.get("synchronized", 0)} '
                    f'actualizadas, {result.get("created", 0)} creadas'
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error sincronizando provincias: {e}'))

    def sync_parques(self, sync_service, force=False):
        """Sincronizar parques nacionales"""
        self.stdout.write('Sincronizando parques nacionales...')
        try:
            result = sync_service.sync_parques_nacionales()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Parques sincronizados: {result.get("synchronized", 0)} '
                    f'actualizados, {result.get("created", 0)} creados'
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error sincronizando parques: {e}'))

    def sync_sitios(self, sync_service, force=False):
        """Sincronizar sitios patrimoniales"""
        self.stdout.write('Sincronizando sitios patrimoniales...')
        try:
            result = sync_service.sync_sitios_patrimoniales()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Sitios sincronizados: {result.get("synchronized", 0)} '
                    f'actualizados, {result.get("created", 0)} creados'
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error sincronizando sitios: {e}'))

    def sync_plazas(self, sync_service, force=False):
        """Sincronizar plazas"""
        self.stdout.write('Sincronizando plazas...')
        try:
            result = sync_service.sync_plazas()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Plazas sincronizadas: {result.get("synchronized", 0)} '
                    f'actualizadas, {result.get("created", 0)} creadas'
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error sincronizando plazas: {e}'))

    @transaction.atomic
    def clean_irrelevant_data(self):
        """Limpiar datos irrelevantes o incompletos"""
        cleaned_count = 0
        
        # Limpiar provincias con nombres vacíos
        count = Provincia.objects.filter(nombre__isnull=True).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminadas {count} provincias sin nombre')
            
        count = Provincia.objects.filter(nombre__exact='').delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminadas {count} provincias con nombre vacío')

        # Limpiar provincias que no son de Ecuador (fuera de la lista oficial)
        ecuador_provinces = [
            'Q220451', 'Q261165', 'Q321729', 'Q335471', 'Q238492', 'Q241140',
            'Q466019', 'Q335526', 'Q335464', 'Q321863', 'Q504238', 'Q504260',
            'Q504666', 'Q549522', 'Q211900', 'Q499475', 'Q214814', 'Q272586',
            'Q475038', 'Q504252', 'Q1124125', 'Q1123208', 'Q499456', 'Q744670'
        ]
        count = Provincia.objects.exclude(wikidata_id__in=ecuador_provinces).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminadas {count} provincias no ecuatorianas')

        # Limpiar parques sin nombre
        count = ParqueNacional.objects.filter(nombre__isnull=True).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminados {count} parques sin nombre')
            
        count = ParqueNacional.objects.filter(nombre__exact='').delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminados {count} parques con nombre vacío')

        # Limpiar parques fuera de Ecuador (coordenadas)
        count = ParqueNacional.objects.filter(latitud__lt=-5.0).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminados {count} parques muy al sur')
            
        count = ParqueNacional.objects.filter(latitud__gt=2.0).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminados {count} parques muy al norte')
            
        count = ParqueNacional.objects.filter(longitud__lt=-92.0).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminados {count} parques muy al oeste')
            
        count = ParqueNacional.objects.filter(longitud__gt=-75.0).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminados {count} parques muy al este')

        # Limpiar sitios patrimoniales sin nombre
        count = SitioPatrimonial.objects.filter(nombre__isnull=True).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminados {count} sitios sin nombre')
            
        count = SitioPatrimonial.objects.filter(nombre__exact='').delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminados {count} sitios con nombre vacío')

        # Limpiar sitios fuera de Ecuador
        count = SitioPatrimonial.objects.filter(latitud__lt=-5.0).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminados {count} sitios muy al sur')
            
        count = SitioPatrimonial.objects.filter(latitud__gt=2.0).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminados {count} sitios muy al norte')
            
        count = SitioPatrimonial.objects.filter(longitud__lt=-92.0).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminados {count} sitios muy al oeste')
            
        count = SitioPatrimonial.objects.filter(longitud__gt=-75.0).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminados {count} sitios muy al este')

        # Limpiar plazas sin nombre
        count = Plaza.objects.filter(nombre__isnull=True).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminadas {count} plazas sin nombre')
            
        count = Plaza.objects.filter(nombre__exact='').delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminadas {count} plazas con nombre vacío')

        # Limpiar plazas fuera de Ecuador
        count = Plaza.objects.filter(latitud__lt=-5.0).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminadas {count} plazas muy al sur')
            
        count = Plaza.objects.filter(latitud__gt=2.0).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminadas {count} plazas muy al norte')
            
        count = Plaza.objects.filter(longitud__lt=-92.0).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminadas {count} plazas muy al oeste')
            
        count = Plaza.objects.filter(longitud__gt=-75.0).delete()[0]
        cleaned_count += count
        if count > 0:
            self.stdout.write(f'Eliminadas {count} plazas muy al este')

        self.stdout.write(
            self.style.SUCCESS(f'Total de registros limpiados: {cleaned_count}')
        )