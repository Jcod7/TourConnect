# Ecuador Tourism - Proyecto Django

Este es un proyecto Django para mostrar información turística y patrimonial del Ecuador.

## Características

- 🏔️ **Provincias del Ecuador**: Información completa de las 24 provincias
- 🌳 **Parques Nacionales**: Datos de áreas protegidas y su biodiversidad
- 🏛️ **Sitios Patrimoniales**: Patrimonio Mundial UNESCO y sitios arqueológicos
- ⛲ **Plazas Principales**: Espacios públicos emblemáticos de las ciudades

## Tecnologías Utilizadas

- **Django 5.2.4**: Framework web de Python
- **Bootstrap 5**: Framework CSS para interfaz responsiva
- **SQLite**: Base de datos por defecto

## Estructura del Proyecto

```
ecuador_sparql/
├── ecuador_sparql/          # Configuración principal del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── ecuador_data/            # Aplicación principal
│   ├── models.py           # Modelos de datos
│   ├── views.py            # Vistas del proyecto
│   ├── urls.py             # URLs de la aplicación
│   ├── admin.py            # Configuración del admin
│   └── templates/          # Templates HTML
├── requirements.txt        # Dependencias del proyecto
└── manage.py              # Script de gestión de Django
```

## Instalación y Configuración

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio** (si está en un repositorio):
   ```bash
   git clone <url-del-repositorio>
   cd ecuador_sparql
   ```

2. **Crear y activar entorno virtual**:
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Linux/Mac:
   source .venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install django requests python-dotenv
   ```

4. **Aplicar migraciones**:
   ```bash
   python manage.py migrate
   ```

5. **Crear superusuario** (opcional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Ejecutar el servidor de desarrollo**:
   ```bash
   python manage.py runserver
   ```

7. **Acceder a la aplicación**:
   - Sitio web: http://127.0.0.1:8000/
   - Admin de Django: http://127.0.0.1:8000/admin/

## Uso de la Aplicación

### Exploración de Datos

- **Provincias**: Explora información detallada de las 24 provincias del Ecuador
- **Parques Nacionales**: Descubre las áreas protegidas del país
- **Sitios Patrimoniales**: Conoce el patrimonio cultural del Ecuador
- **Plazas**: Recorre los espacios públicos más importantes

### API REST

El proyecto incluye endpoints de API para acceso programático:

- `/api/provincias/`: Lista todas las provincias
- `/api/parques/`: Lista todos los parques nacionales

## Modelos de Datos

### Provincia
- Nombre, capital, población, área
- Coordenadas geográficas
- URLs de imagen, bandera y escudo
- ID de Wikidata para referencia

### ParqueNacional
- Nombre, descripción, área
- Fecha de establecimiento
- Provincia, coordenadas
- URLs de imagen y sitio web

### SitioPatrimonial
- Nombre, tipo (UNESCO, Arqueológico, Histórico)
- Descripción, coordenadas
- URL de imagen

### Plaza
- Nombre, ciudad
- Coordenadas geográficas
- URL de imagen

## Características Técnicas

### Interfaz Web
- Diseño responsivo con Bootstrap 5
- Navegación intuitiva
- Paginación automática
- Integración con mapas (OpenStreetMap)

### Panel de Administración
- Gestión completa de datos
- Filtros y búsquedas avanzadas
- Importación/exportación de datos

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Fuentes de Datos

- **Wikidata**: https://www.wikidata.org/ (Licencia CC0)
- **DBpedia**: https://dbpedia.org/ (Licencias varias, principalmente CC-BY-SA)

## Contacto

Para preguntas o sugerencias sobre este proyecto, por favor abre un issue en el repositorio.

---

Desarrollado con ❤️ utilizando Django para explorar el patrimonio ecuatoriano.
