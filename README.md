# 🕷️ Scraper de Noticias Multi-Fuente

Sistema completo de scraping para extraer noticias de 11 fuentes especializadas en tecnología, IA y actualidad.

## 📰 Fuentes Configuradas

1. **Supply Chain Digital** - https://supplychaindigital.com/
2. **UNESCO** - https://www.unesco.org/en
3. **Infobae** - https://www.infobae.com/
4. **Xataka** - https://www.xataka.com/
5. **Genbeta** - https://www.genbeta.com/
6. **Hipertextual** - https://hipertextual.com/
7. **TechCrunch** - https://techcrunch.com/
8. **The Verge** - https://www.theverge.com/
9. **OpenAI News** - https://openai.com/es-419/news/
10. **Anthropic Engineering** - https://www.anthropic.com/engineering
11. **DeepMind Blog** - https://deepmind.google/blog/

## 🚀 Instalación Rápida

```bash
# 1. Navegar a la carpeta
cd "c:\Users\PASANTE 2\Documents\scraper"

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar el scraper
python ejecutar_busquedas.py
```

## 💡 Modos de Uso

### Opción 1: Ejecutar Todas las Búsquedas Predefinidas

```bash
python ejecutar_busquedas.py
# Seleccionar opción 1
```

**Búsquedas incluidas:**
- ✅ Inteligencia Artificial
- ✅ China y la IA
- ✅ Blockchain y Criptomonedas
- ✅ Robótica y Automatización
- ✅ Cambio Climático y Sostenibilidad

**Resultado:** Genera archivos JSON individuales para cada búsqueda + un archivo consolidado.

### Opción 2: Búsqueda Personalizada

```bash
python ejecutar_busquedas.py
# Seleccionar opción 2
# Ingresar tema y palabras clave
```

### Opción 3: Solo IA

```bash
python ejecutar_busquedas.py
# Seleccionar opción 3
```

### Opción 4: Solo China y IA

```bash
python ejecutar_busquedas.py
# Seleccionar opción 4
```

## 🔧 Uso Programático

### Ejemplo Básico

```python
from news_sources_scraper import NewsSourcesScraper

# Crear scraper
scraper = NewsSourcesScraper()

# Definir palabras clave
keywords = ['IA', 'inteligencia artificial', 'AI', 'ChatGPT']

# Ejecutar búsqueda
resultado = scraper.generate_search_result(
    search_query="Inteligencia Artificial",
    keywords=keywords
)

# Guardar resultados
scraper.save_results(resultado, 'mi_busqueda.json')

# Acceder a los hallazgos
print(f"Total de artículos: {resultado['total_hallazgos']}")
for hallazgo in resultado['hallazgos']:
    print(f"- {hallazgo['titulo']}")
    print(f"  Fuente: {hallazgo['fuente']}")
    print(f"  URL: {hallazgo['url']}")
```

### Ejemplo Avanzado - Scraping de Fuente Individual

```python
from news_sources_scraper import NewsSourcesScraper

scraper = NewsSourcesScraper()

# Scrapear solo TechCrunch
resultado = scraper.scrape_source(
    url="https://techcrunch.com/",
    keywords=['startup', 'funding', 'AI']
)

print(f"Artículos encontrados: {resultado['articulos_encontrados']}")

for articulo in resultado['articulos']:
    print(f"\n{articulo['titulo']}")
    print(f"URL: {articulo['url']}")
    print(f"Descripción: {articulo['descripcion']}")
```

### Ejemplo - Scraping de Todas las Fuentes sin Filtro

```python
from news_sources_scraper import NewsSourcesScraper

scraper = NewsSourcesScraper()

# Scrapear todas las fuentes sin filtrar por keywords
resultados = scraper.scrape_all_sources(
    keywords=None,  # Sin filtro
    delay=2.0  # 2 segundos entre requests
)

# Procesar resultados
for fuente in resultados:
    print(f"\n{fuente['nombre_fuente']}")
    print(f"  Estado: {fuente['estado']}")
    print(f"  Artículos: {fuente['articulos_encontrados']}")
```

## 📊 Estructura del JSON Generado

```json
{
  "busqueda_realizada": "Inteligencia Artificial",
  "timestamp": "2025-12-22T09:38:00.000000",
  "total_fuentes_consultadas": 11,
  "fuentes_exitosas": 10,
  "total_hallazgos": 45,
  "hallazgos": [
    {
      "fuente": "TechCrunch",
      "url_fuente": "https://techcrunch.com/",
      "titulo": "OpenAI lanza nuevo modelo GPT-5",
      "url": "https://techcrunch.com/2025/...",
      "descripcion": "OpenAI ha anunciado...",
      "imagen": "https://...",
      "fecha": "2025-12-22",
      "relevancia": 5
    }
  ],
  "detalle_por_fuente": [
    {
      "fuente": "https://techcrunch.com/",
      "nombre_fuente": "Techcrunch",
      "estado": "completado",
      "articulos_encontrados": 8,
      "articulos": [...]
    }
  ]
}
```

### Campos Explicados

| Campo | Descripción |
|-------|-------------|
| `busqueda_realizada` | Tema de la búsqueda |
| `timestamp` | Fecha y hora de la búsqueda |
| `total_fuentes_consultadas` | Número de fuentes intentadas |
| `fuentes_exitosas` | Fuentes que respondieron exitosamente |
| `total_hallazgos` | Artículos encontrados que coinciden con keywords |
| `hallazgos` | Array con todos los artículos relevantes |
| `relevancia` | Puntuación basada en coincidencia de keywords |
| `detalle_por_fuente` | Información detallada de cada fuente |

## 📁 Archivos Generados

Después de ejecutar el scraper, se generan:

### Búsqueda Individual
- `busqueda_inteligencia_artificial.json`
- `busqueda_china_y_la_ia.json`
- `busqueda_blockchain_y_criptomonedas.json`
- etc.

### Archivo Consolidado
- `todas_las_busquedas.json` - Contiene todas las búsquedas en un solo archivo

### Búsqueda Personalizada
- `busqueda_personalizada_[tema].json`

## ⚙️ Configuración

### Modificar Fuentes

Edita el archivo `news_sources_scraper.py`:

```python
class NewsSourcesScraper:
    SOURCES = [
        "https://tu-nueva-fuente.com/",
        # ... más fuentes
    ]
```

### Ajustar Delay Entre Requests

```python
# En ejecutar_busquedas.py o en uso programático
resultados = scraper.scrape_all_sources(
    keywords=keywords,
    delay=3.0  # Aumentar a 3 segundos
)
```

### Personalizar Keywords para Búsqueda

Edita el archivo `ejecutar_busquedas.py`:

```python
BUSQUEDAS = [
    {
        'nombre': 'Tu Tema',
        'keywords': [
            'keyword1', 'keyword2', 'keyword3'
        ]
    }
]
```

## 🎯 Características Principales

✅ **Scraping Inteligente**
- Detección automática de artículos con selectores genéricos
- Extracción de título, descripción, imagen, fecha y URL
- Compatible con múltiples estructuras HTML

✅ **Filtrado por Relevancia**
- Sistema de puntuación basado en keywords
- Ordenamiento automático por relevancia
- Filtrado flexible con múltiples palabras clave

✅ **Manejo Robusto de Errores**
- Timeouts configurables
- Continuación automática ante fallos
- Registro de estado por fuente

✅ **Exportación Estructurada**
- Formato JSON estandarizado
- Archivos individuales y consolidados
- Metadatos completos de cada búsqueda

## 🔍 Casos de Uso

### 1. Monitoreo de Noticias de IA
```bash
python ejecutar_busquedas.py
# Opción 3 - Solo Inteligencia Artificial
```

### 2. Análisis de Competencia (China)
```bash
python ejecutar_busquedas.py
# Opción 4 - China y la IA
```

### 3. Investigación de Tendencias
```bash
python ejecutar_busquedas.py
# Opción 2 - Búsqueda personalizada
# Ej: "Quantum Computing", keywords: quantum, qubit, etc.
```

### 4. Agregación de Noticias Diarias
```python
# Script automatizado
from news_sources_scraper import NewsSourcesScraper
from datetime import datetime

scraper = NewsSourcesScraper()
resultado = scraper.generate_search_result(
    search_query=f"Noticias Diarias - {datetime.now().date()}",
    keywords=None  # Sin filtro, todas las noticias
)

scraper.save_results(resultado, f"noticias_{datetime.now().date()}.json")
```

## 📈 Mejores Prácticas

1. **Respetar Rate Limits**
   - Usa delays de al menos 1-2 segundos entre requests
   - No ejecutes el script con demasiada frecuencia

2. **Keywords Efectivas**
   - Usa variaciones del término (ej: "IA", "AI", "inteligencia artificial")
   - Incluye términos en inglés y español
   - Añade nombres de empresas/productos relacionados

3. **Verificación de Resultados**
   - Revisa manualmente algunos artículos
   - Ajusta keywords si hay demasiados falsos positivos

4. **Almacenamiento**
   - Los JSON pueden ser grandes, considera comprimir archivos antiguos
   - Implementa rotación de archivos para uso continuo

## 🛠️ Solución de Problemas

### Error: "Request timeout"
- **Causa**: Fuente lenta o inaccesible
- **Solución**: El scraper continúa automáticamente con la siguiente fuente

### Pocos resultados encontrados
- **Causa**: Keywords muy específicas o artículos recientes no disponibles
- **Solución**: Amplía las keywords o ejecuta sin filtro

### "No se encontraron artículos"
- **Causa**: Cambio en estructura HTML del sitio
- **Solución**: El scraper usa selectores genéricos, pero algunos sitios pueden requerir ajustes manuales

## 📝 Notas Importantes

- ⚠️ **Uso Ético**: Este scraper es para uso educativo y de investigación
- ⚠️ **Respeta robots.txt**: Verifica que los sitios permitan scraping
- ⚠️ **Rate Limiting**: No sobrecargues los servidores
- ⚠️ **Términos de Servicio**: Revisa los ToS de cada sitio

## 🔄 Actualización de Dependencias

```bash
pip install --upgrade -r requirements.txt
```

## 📄 Licencia

Uso educativo y personal.

---

**Desarrollado para consultar noticias de tecnología, IA y actualidad de múltiples fuentes especializadas.**
