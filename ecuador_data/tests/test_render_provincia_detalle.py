from django.test import TestCase
from ecuador_data.models import Provincia

class ProvinciaDetalleRenderTest(TestCase):
    def setUp(self):
        Provincia.objects.create(
            nombre="Guayas",
            capital="Guayaquil",
            poblacion=4000000,
            area=15000.5,
            latitud=-2.18,
            longitud=-79.88,
            imagen_url="https://upload.wikimedia.org/wikipedia/commons/1/1a/Guayas.jpg",
            bandera_url="https://upload.wikimedia.org/wikipedia/commons/2/2a/Flag_of_Guayas.svg",
            wikidata_id="Q14594",
            cantones=[
                {"nombre": "Guayaquil", "cabecera": "Guayaquil", "poblacion": "2350915"},
                {"nombre": "Samborondón", "cabecera": "Samborondón", "poblacion": "80000"},
                {"nombre": "Durán", "cabecera": "Durán", "poblacion": "315000"}
            ]
        )

    def test_provincia_detalle_renderiza_cantones(self):
        provincia = Provincia.objects.get(nombre="Guayas")
        response = self.client.get(f'/provincias/{provincia.pk}/')
        self.assertContains(response, "Cantones de Guayas")
        self.assertContains(response, "Guayaquil")
        self.assertContains(response, "Samborondón")
        self.assertContains(response, "Durán")
