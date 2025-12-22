"""
Script para realizar búsquedas por tema
Extrae noticias de múltiples fuentes sobre un tema específico
"""

from news_sources_scraper import NewsSourcesScraper
import sys
from datetime import datetime


def ejecutar_busqueda(tema: str, keywords: list = None):
    """
    Ejecuta una búsqueda por tema
    
    Args:
        tema: Tema de búsqueda
        keywords: Lista de palabras clave (opcional, si no se proporciona usa el tema)
    """
    scraper = NewsSourcesScraper()
    
    print("=" * 70)
    print("   🕷️  SCRAPER DE NOTICIAS MULTI-FUENTE")
    print("=" * 70)
    print(f"\n📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔍 Tema de búsqueda: {tema}")
    
    # Si no se proporcionan keywords, usar el tema
    if not keywords:
        keywords = [tema]
    
    print(f"📌 Palabras clave: {', '.join(keywords)}\n")
    
    # Ejecutar búsqueda
    resultado = scraper.generate_search_result(
        search_query=tema,
        keywords=keywords
    )
    
    # Guardar resultado
    filename = f"busqueda_{tema.lower().replace(' ', '_').replace('/', '_')}.json"
    scraper.save_results(resultado, filename)
    
    # Mostrar resumen
    print(f"\n{'='*70}")
    print("📊 RESULTADOS")
    print(f"{'='*70}")
    print(f"Total de hallazgos: {resultado['total_hallazgos']}")
    print(f"Fuentes exitosas: {resultado['fuentes_exitosas']}/{resultado['total_fuentes_consultadas']}")
    
    if resultado['total_hallazgos'] > 0:
        print(f"\n📰 Artículos encontrados:\n")
        for i, hallazgo in enumerate(resultado['hallazgos'][:10], 1):
            print(f"{i}. {hallazgo['titulo']}")
            print(f"   Fuente: {hallazgo['fuente']}")
            print(f"   URL: {hallazgo['url']}")
            if hallazgo.get('contenido'):
                print(f"   Contenido: {len(hallazgo['contenido'])} caracteres extraídos")
            print()
    
    print(f"\n{'='*70}")
    print("✅ Proceso finalizado")
    print(f"{'='*70}\n")
    
    return resultado


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("=" * 70)
        print("   🕷️  SCRAPER DE NOTICIAS MULTI-FUENTE")
        print("=" * 70)
        print("\n📖 USO:")
        print("   python ejecutar_busquedas.py \"<tema>\" [keyword1] [keyword2] ...")
        print("\n📝 EJEMPLOS:")
        print("   python ejecutar_busquedas.py \"Inteligencia Artificial\"")
        print("   python ejecutar_busquedas.py \"Inteligencia Artificial\" \"IA\" \"AI\" \"machine learning\"")
        print("   python ejecutar_busquedas.py \"Cambio climático\"")
        print("   python ejecutar_busquedas.py \"Tecnología\" \"tech\" \"innovación\"")
        print("\n💡 NOTA: El tema debe ir entre comillas dobles si contiene espacios")
        print("=" * 70)
        sys.exit(1)
    
    tema = sys.argv[1]
    keywords = sys.argv[2:] if len(sys.argv) > 2 else None
    
    ejecutar_busqueda(tema, keywords)
