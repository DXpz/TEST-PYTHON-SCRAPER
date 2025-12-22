# 🚀 GUÍA DE INICIO RÁPIDO

## ⚠️ Requisito Previo: Instalar Python

Antes de usar el scraper, necesitas tener Python instalado.

### Opción 1: Descargar Python (Recomendado)
1. Ve a: https://www.python.org/downloads/
2. Descarga Python 3.11 o superior
3. **IMPORTANTE**: Durante la instalación, marca ✅ "Add Python to PATH"
4. Completa la instalación

### Opción 2: Desde Microsoft Store
1. Abre Microsoft Store
2. Busca "Python 3.11" o "Python 3.12"
3. Instala

## 📦 Instalación de Dependencias

Una vez que Python esté instalado, abre PowerShell o CMD en esta carpeta y ejecuta:

```bash
pip install -r requirements.txt
```

O si eso no funciona:

```bash
python -m pip install -r requirements.txt
```

## ✅ Verificar Instalación

```bash
python --version
```

Deberías ver algo como: `Python 3.11.x` o `Python 3.12.x`

## 🎯 EJECUTAR EL SCRAPER

### Modo Interactivo (Recomendado para empezar)

```bash
python ejecutar_busquedas.py
```

Te aparecerá un menú:
```
Opciones:
  1. Ejecutar todas las búsquedas predefinidas
  2. Ejecutar búsqueda personalizada
  3. Solo búsqueda de Inteligencia Artificial
  4. Solo búsqueda de China y la IA

Selecciona una opción (1-4):
```

### Opción 1: Todas las Búsquedas
- Ejecuta 5 búsquedas predefinidas
- Genera archivos JSON para cada una
- Crea un archivo consolidado

**Tiempo estimado**: 5-10 minutos (depende de la velocidad de internet)

### Opción 2: Búsqueda Personalizada
Te pedirá:
1. Tema de búsqueda
2. Palabras clave (separadas por comas)

Ejemplo:
```
Tema: Vehículos Eléctricos
Keywords: Tesla, EV, coche eléctrico, batería, autonomía
```

### Opción 3: Solo IA
Búsqueda rápida enfocada en Inteligencia Artificial

### Opción 4: China y IA
Búsqueda sobre desarrollos de IA en China

## 📊 Resultados

Los archivos JSON se guardarán en esta misma carpeta:

```
scraper/
├── busqueda_inteligencia_artificial.json
├── busqueda_china_y_la_ia.json
├── busqueda_blockchain_y_criptomonedas.json
├── busqueda_robotica_y_automatizacion.json
├── busqueda_cambio_climatico_y_sostenibilidad.json
└── todas_las_busquedas.json  ← Archivo consolidado
```

## 📖 Ejemplo de Uso Programático

Si quieres usar el scraper en tu propio código Python:

```python
from news_sources_scraper import NewsSourcesScraper

# Crear scraper
scraper = NewsSourcesScraper()

# Definir búsqueda
keywords = ['ChatGPT', 'GPT-4', 'OpenAI', 'IA generativa']

# Ejecutar
resultado = scraper.generate_search_result(
    search_query="GPT y Modelos de Lenguaje",
    keywords=keywords
)

# Guardar
scraper.save_results(resultado, 'mi_busqueda.json')

# Ver resultados
print(f"Encontrados: {resultado['total_hallazgos']} artículos")

for articulo in resultado['hallazgos'][:5]:  # Top 5
    print(f"\n{articulo['titulo']}")
    print(f"Fuente: {articulo['fuente']}")
    print(f"URL: {articulo['url']}")
```

## 🌐 Fuentes Consultadas

El scraper consulta automáticamente estas 11 fuentes:

1. ✅ Supply Chain Digital
2. ✅ UNESCO
3. ✅ Infobae
4. ✅ Xataka
5. ✅ Genbeta
6. ✅ Hipertextual
7. ✅ TechCrunch
8. ✅ The Verge
9. ✅ OpenAI News
10. ✅ Anthropic Engineering
11. ✅ DeepMind Blog

## ⏱️ Tiempos Estimados

- **Una fuente**: ~5-10 segundos
- **Todas las fuentes (11)**: ~2-3 minutos
- **Búsqueda completa con todas las fuentes**: ~3-5 minutos
- **5 búsquedas predefinidas**: ~10-15 minutos

## 🔧 Solución de Problemas

### "Python no se reconoce como comando"
- Python no está instalado o no está en el PATH
- Reinstala Python marcando "Add to PATH"

### "pip no se reconoce como comando"
- Usa: `python -m pip install -r requirements.txt`

### Error de timeout en alguna fuente
- Es normal, el scraper continúa con las demás fuentes
- Algunas fuentes pueden estar temporalmente lentas

### No encuentra artículos
- Las keywords pueden ser muy específicas
- Prueba con keywords más generales
- Ejecuta sin filtro (keywords=None en código)

## 💡 Consejos

1. **Primera vez**: Ejecuta opción 3 (Solo IA) para probar rápidamente
2. **Keywords efectivas**: Usa tanto términos en español como inglés
3. **Horarios**: Ejecuta cuando tengas buena conexión a internet
4. **Frecuencia**: No ejecutes muy seguido para respetar los servidores

## 📞 Ayuda Adicional

Consulta el archivo `README.md` para documentación completa y ejemplos avanzados.

---

**¿Listo para empezar?**

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar scraper
python ejecutar_busquedas.py

# 3. Seleccionar opción 3 para una prueba rápida
```

¡Eso es todo! 🎉
