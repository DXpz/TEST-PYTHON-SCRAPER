"""
Script para probar una fuente individual antes de agregarla al scraper principal
Verifica robots.txt y prueba el scraping
"""

from news_sources_scraper import NewsSourcesScraper
from urllib.parse import urlparse
import sys


def probar_fuente(url: str, tema: str = None, keywords: list = None):
    """
    Prueba una fuente individual
    
    Args:
        url: URL de la fuente a probar
        tema: Tema opcional para búsqueda
        keywords: Keywords opcionales para búsqueda
    """
    print("=" * 70)
    print("   🧪 PROBADOR DE FUENTE INDIVIDUAL")
    print("=" * 70)
    print(f"\n🔗 URL a probar: {url}")
    
    # Validar URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            print("\n❌ URL inválida. Debe incluir http:// o https://")
            return False
    except Exception as e:
        print(f"\n❌ Error validando URL: {str(e)}")
        return False
    
    # Crear scraper
    scraper = NewsSourcesScraper()
    
    print(f"\n📋 Verificando robots.txt...")
    print(f"🤖 User-Agent: {scraper.user_agent}")
    
    # Verificar robots.txt
    puede_acceder = scraper.check_robots_txt(url)
    
    if not puede_acceder:
        print(f"\n🚫 robots.txt BLOQUEA el acceso a esta URL")
        print(f"⚠️  No se recomienda agregar esta fuente al scraper principal")
        respuesta = input("\n¿Deseas continuar de todas formas? (s/n): ").strip().lower()
        if respuesta != 's':
            return False
    else:
        print(f"✅ robots.txt PERMITE el acceso a esta URL")
    
    # Probar scraping
    print(f"\n🕷️  Iniciando prueba de scraping...")
    print(f"{'='*70}\n")
    
    try:
        # Probar acceso básico primero
        print(f"🔍 Probando acceso a la URL...")
        soup = scraper.fetch_page(url, check_robots=False)  # Ya verificamos robots.txt arriba
        
        if soup is None:
            print(f"\n❌ No se pudo acceder a la URL")
            print(f"   Esto significa que:")
            print(f"   - El sitio bloquea el scraper (Connection reset)")
            print(f"   - La URL no es accesible")
            print(f"   - Hay problemas de conexión")
            print(f"   - El sitio requiere JavaScript (el scraper no ejecuta JS)")
            print(f"\n⚠️  RECOMENDACIÓN: No agregar esta fuente al scraper principal")
            return False
        
        print(f"✅ Acceso a la URL exitoso")
        
        # Hacer scraping de la fuente
        resultado = scraper.scrape_source(url, keywords=keywords, tema=tema)
        
        print(f"\n{'='*70}")
        print("📊 RESULTADOS DE LA PRUEBA")
        print(f"{'='*70}")
        print(f"Estado: {resultado['estado']}")
        print(f"Artículos encontrados: {resultado['articulos_encontrados']}")
        print(f"Nombre de la fuente: {resultado['nombre_fuente']}")
        
        if resultado['estado'] == 'error':
            print(f"\n❌ Error al scrapear la fuente")
            print(f"   El acceso fue exitoso pero no se pudieron extraer artículos")
            print(f"   Posibles causas:")
            print(f"   - La estructura HTML del sitio es diferente")
            print(f"   - Los selectores no funcionan con este sitio")
            print(f"   - El sitio carga contenido dinámicamente con JavaScript")
            print(f"   - No hay artículos en la página principal")
            print(f"\n⚠️  RECOMENDACIÓN: El sitio es accesible pero necesita selectores personalizados")
            return False
        
        if resultado['articulos_encontrados'] == 0:
            print(f"\n⚠️  No se encontraron artículos")
            print(f"   Esto puede ser normal si:")
            print(f"   - El sitio tiene una estructura diferente")
            print(f"   - No hay artículos en la página principal")
            print(f"   - Los filtros de keywords son muy restrictivos")
        else:
            print(f"\n✅ Se encontraron {resultado['articulos_encontrados']} artículos")
            print(f"\n📰 Primeros 5 artículos encontrados:")
            for i, articulo in enumerate(resultado['articulos'][:5], 1):
                print(f"\n  {i}. {articulo['titulo']}")
                print(f"     URL: {articulo['url']}")
                if articulo.get('descripcion'):
                    print(f"     Descripción: {articulo['descripcion'][:100]}...")
        
        # Mostrar resumen
        print(f"\n{'='*70}")
        print("📝 RESUMEN")
        print(f"{'='*70}")
        print(f"✅ robots.txt: {'PERMITIDO' if puede_acceder else 'BLOQUEADO'}")
        print(f"✅ Estado scraping: {resultado['estado']}")
        print(f"✅ Artículos encontrados: {resultado['articulos_encontrados']}")
        
        if resultado['articulos_encontrados'] > 0 and puede_acceder:
            print(f"\n✅ RECOMENDACIÓN: Esta fuente puede agregarse al scraper principal")
        elif resultado['articulos_encontrados'] == 0:
            print(f"\n⚠️  RECOMENDACIÓN: Probar con diferentes keywords o verificar la estructura del sitio")
        else:
            print(f"\n❌ RECOMENDACIÓN: No se recomienda agregar esta fuente")
        
        return resultado['articulos_encontrados'] > 0 and puede_acceder
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("   🧪 PROBADOR DE FUENTE INDIVIDUAL")
    print("=" * 70)
    print("\nEste script te permite probar una fuente antes de agregarla")
    print("al scraper principal. Verifica robots.txt y prueba el scraping.\n")
    
    # Solicitar URL
    url = input("🔗 Ingresa la URL de la fuente a probar: ").strip()
    
    if not url:
        print("\n❌ No se ingresó ninguna URL")
        sys.exit(1)
    
    # Agregar http:// si no tiene protocolo
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"   (Agregado https:// -> {url})")
    
    # Preguntar por tema/keywords opcionales
    print("\n💡 Búsqueda opcional (presiona Enter para omitir):")
    tema = input("   Tema: ").strip() or None
    keywords_input = input("   Keywords (separadas por comas): ").strip()
    
    keywords = None
    if keywords_input:
        keywords = [kw.strip() for kw in keywords_input.split(',') if kw.strip()]
    
    # Ejecutar prueba
    exito = probar_fuente(url, tema=tema, keywords=keywords)
    
    # Resultado final
    print(f"\n{'='*70}")
    if exito:
        print("✅ PRUEBA EXITOSA")
        print("   Puedes agregar esta fuente al scraper principal")
    else:
        print("❌ PRUEBA FALLIDA O NO RECOMENDADA")
        print("   Revisa los resultados antes de agregar esta fuente")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba interrumpida por el usuario\n")
        sys.exit(0)

