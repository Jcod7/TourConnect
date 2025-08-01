# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Setup and Dependencies:**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install django requests python-dotenv SPARQLWrapper
```

**Database Management:**
```bash
# Apply database migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

**Development Server:**
```bash
# Run development server
python manage.py runserver

# Access points:
# - Main site: http://127.0.0.1:8000/
# - Django admin: http://127.0.0.1:8000/admin/
```

**Testing:**
```bash
# Run tests
python manage.py test

# Run specific test
python manage.py test ecuador_data.tests.test_render_provincia_detalle
```

## Architecture Overview

This is a Django 5.2.4 application that displays tourist and heritage information about Ecuador using SPARQL queries to external knowledge bases.

**Core Architecture Pattern:**
- **Data Sources**: External SPARQL endpoints (Wikidata, DBpedia)
- **Data Layer**: Django models with automatic synchronization from SPARQL
- **Service Layer**: SPARQL service classes that encapsulate knowledge base queries
- **Presentation Layer**: Django views with Bootstrap 5 templates

**Key Components:**

1. **SPARQL Services** (`ecuador_data/sparql_services.py`):
   - `WikidataService`: Queries Wikidata for structured data
   - `DBpediaService`: Queries DBpedia for additional information
   - `DataSyncService`: Orchestrates data synchronization between external sources and local models

2. **Data Models** (`ecuador_data/models.py`):
   - `Provincia`: 24 provinces with capitals, coordinates, population, area, and canton subdivisions
   - `ParqueNacional`: National parks with establishment dates and geographic data
   - `SitioPatrimonial`: Heritage sites (UNESCO, archaeological, historical)
   - `Plaza`: Public squares in Ecuadorian cities

3. **Auto-sync Pattern**: Views automatically trigger data synchronization from external sources before displaying content, ensuring fresh data without manual intervention.

**Data Flow:**
1. User requests a page → View triggers sync → SPARQL queries execute → Local models update → Template renders with current data

**Important Technical Details:**
- Uses SQLite for local data storage with automatic updates from SPARQL endpoints
- Implements coordinate parsing from Wikidata's "Point(longitude latitude)" format
- Handles bilingual data (Spanish/English) from different knowledge bases
- Canton data is stored as JSONField with nested properties (nombre, descripcion, cabecera, poblacion, etc.)
- All models include `wikidata_id` for external reference tracking

**Template Structure:**
- Base template with Bootstrap 5 integration
- List views with pagination (12 items per page for provinces)
- Detail views with geographic coordinate display
- OpenStreetMap integration for location visualization