# Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

Este es un proyecto Django que utiliza consultas SPARQL para obtener datos turísticos de Ecuador desde Wikidata y DBpedia.

## Contexto del Proyecto
- **Framework**: Django
- **Propósito**: Consultar y mostrar información turística de Ecuador
- **Fuentes de datos**: Wikidata y DBpedia
- **Tecnología SPARQL**: SPARQLWrapper para consultas

## Estructura de datos
- **Provincias**: Información de las 24 provincias del Ecuador
- **Parques Nacionales**: Datos de parques nacionales ecuatorianos
- **Sitios Patrimoniales**: Patrimonio Mundial UNESCO y sitios arqueológicos
- **Plazas**: Plazas principales de ciudades ecuatorianas

## Patrones de código
- Usar clases de servicio para encapsular consultas SPARQL
- Implementar manejo de errores para consultas fallidas
- Cachear resultados cuando sea apropiado
- Seguir convenciones de Django para vistas y modelos
