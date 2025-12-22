"""
Script para realizar búsquedas temáticas personalizadas
Permite ejecutar múltiples búsquedas con diferentes temas
"""

from news_sources_scraper import NewsSourcesScraper
import json
from datetime import datetime


# Definir búsquedas temáticas
BUSQUEDAS = [
    {
        'nombre': 'Inteligencia Artificial',
        'keywords': [
            'inteligencia artificial', 'IA', 'AI', 
            'machine learning', 'deep learning', 
            'GPT', 'LLM', 'ChatGPT', 'OpenAI', 
            'Anthropic', 'Claude', 'Gemini',
            'modelo de lenguaje', 'neural network',
            'aprendizaje automático'
        ]
    },
    {
        'nombre': 'China y la IA',
        'keywords': [
            'China', 'chino', 'Beijing', 'Shanghai',
            'Alibaba', 'Baidu', 'Tencent', 'Huawei',
            'IA China', 'AI China', 'tecnología china',
            'DeepSeek', 'SenseTime'
        ]
    },
    {
        'nombre': 'Blockchain y Criptomonedas',
        'keywords': [
            'blockchain', 'bitcoin', 'ethereum',
            'criptomoneda', 'crypto', 'NFT',
            'Web3', 'DeFi', 'smart contract'
        ]
    },
    {
        'nombre': 'Robótica y Automatización',
        'keywords': [
            'robot', 'robótica', 'automatización',
            'automation', 'drones', 'vehículos autónomos',
            'cobot', 'industrial automation'
        ]
    },
    {
        'nombre': 'Cambio Climático y Sostenibilidad',
        'keywords': [
            'cambio climático', 'sostenibilidad',
            'energía renovable', 'emisiones',
            'carbono', 'medio ambiente',
            'sustentabilidad', 'green tech'
        ]
    }
]


def ejecutar_busqueda_individual(scraper, busqueda_config):
    """
    Ejecuta una búsqueda individual
    """
    print(f"\n{'='*70}")
    print(f"🔍 Búsqueda: {busqueda_config['nombre']}")
    print(f"{'='*70}\n")
    
    resultado = scraper.generate_search_result(
        search_query=busqueda_config['nombre'],
        keywords=busqueda_config['keywords']
    )
    
    # Guardar resultado individual
    filename = f"busqueda_{busqueda_config['nombre'].lower().replace(' ', '_')}.json"
    scraper.save_results(resultado, filename)
    
    return resultado


def ejecutar_todas_las_busquedas():
    """
    Ejecuta todas las búsquedas configuradas
    """
    scraper = NewsSourcesScraper()
    
    print("=" * 70)
    print("   SCRAPER DE NOTICIAS - BÚSQUEDAS TEMÁTICAS")
    print("=" * 70)
    print(f"\n📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📚 Total de búsquedas a realizar: {len(BUSQUEDAS)}")
    print(f"🌐 Fuentes configuradas: {len(NewsSourcesScraper.SOURCES)}\n")
    
    # Almacenar todos los resultados
    resultados_completos = []
    
    # Ejecutar cada búsqueda
    for i, busqueda in enumerate(BUSQUEDAS, 1):
        print(f"\n[{i}/{len(BUSQUEDAS)}] ", end='')
        
        resultado = ejecutar_busqueda_individual(scraper, busqueda)
        
        resultados_completos.append({
            'busqueda': busqueda['nombre'],
            'resultado': resultado
        })
        
        # Mostrar resumen
        print(f"\n📊 Resumen:")
        print(f"   • Hallazgos encontrados: {resultado['total_hallazgos']}")
        print(f"   • Fuentes exitosas: {resultado['fuentes_exitosas']}/{resultado['total_fuentes_consultadas']}")
        
        if resultado['total_hallazgos'] > 0:
            print(f"\n   📰 Top 3 artículos:")
            for j, hallazgo in enumerate(resultado['hallazgos'][:3], 1):
                print(f"      {j}. {hallazgo['titulo'][:70]}...")
                print(f"         Fuente: {hallazgo['fuente']}")
    
    # Guardar todos los resultados en un solo archivo
    archivo_completo = {
        'timestamp': datetime.now().isoformat(),
        'total_busquedas': len(BUSQUEDAS),
        'busquedas': resultados_completos
    }
    
    with open('todas_las_busquedas.json', 'w', encoding='utf-8') as f:
        json.dump(archivo_completo, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*70}")
    print("✅ TODAS LAS BÚSQUEDAS COMPLETADAS")
    print(f"{'='*70}")
    print(f"\n💾 Archivos generados:")
    print(f"   • todas_las_busquedas.json (archivo consolidado)")
    for busqueda in BUSQUEDAS:
        filename = f"busqueda_{busqueda['nombre'].lower().replace(' ', '_')}.json"
        print(f"   • {filename}")
    
    print(f"\n📊 Resumen general:")
    total_hallazgos = sum(r['resultado']['total_hallazgos'] for r in resultados_completos)
    print(f"   • Total de hallazgos en todas las búsquedas: {total_hallazgos}")
    print(f"   • Promedio de hallazgos por búsqueda: {total_hallazgos / len(BUSQUEDAS):.1f}")


def ejecutar_busqueda_personalizada():
    """
    Permite al usuario ejecutar una búsqueda personalizada
    """
    import sys
    
    scraper = NewsSourcesScraper()
    
    print("=" * 70)
    print("   BÚSQUEDA PERSONALIZADA")
    print("=" * 70)
    print()
    
    # Solicitar tema de búsqueda
    tema = input("📝 Ingresa el tema de búsqueda: ").strip()
    
    if not tema:
        print("❌ Debes ingresar un tema")
        return
    
    # Solicitar palabras clave
    print("\n🔑 Ingresa las palabras clave (separadas por comas):")
    keywords_input = input("   > ").strip()
    
    if not keywords_input:
        keywords = [tema]
    else:
        keywords = [k.strip() for k in keywords_input.split(',')]
    
    print(f"\n🔍 Buscando artículos sobre: {tema}")
    print(f"📌 Palabras clave: {', '.join(keywords)}\n")
    
    # Ejecutar búsqueda
    resultado = scraper.generate_search_result(
        search_query=tema,
        keywords=keywords
    )
    
    # Guardar resultado
    filename = f"busqueda_personalizada_{tema.lower().replace(' ', '_')}.json"
    scraper.save_results(resultado, filename)
    
    # Mostrar resultados
    print(f"\n{'='*70}")
    print("📊 RESULTADOS")
    print(f"{'='*70}")
    print(f"Total de hallazgos: {resultado['total_hallazgos']}")
    
    if resultado['total_hallazgos'] > 0:
        print(f"\n📰 Artículos encontrados:\n")
        for i, hallazgo in enumerate(resultado['hallazgos'][:10], 1):
            print(f"{i}. {hallazgo['titulo']}")
            print(f"   Fuente: {hallazgo['fuente']}")
            print(f"   URL: {hallazgo['url']}")
            if hallazgo['descripcion']:
                print(f"   {hallazgo['descripcion'][:150]}...")
            print()


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("   🕷️  SCRAPER DE NOTICIAS MULTI-FUENTE")
    print("="*70 + "\n")
    
    print("Opciones:")
    print("  1. Ejecutar todas las búsquedas predefinidas")
    print("  2. Ejecutar búsqueda personalizada")
    print("  3. Solo búsqueda de Inteligencia Artificial")
    print("  4. Solo búsqueda de China y la IA")
    print()
    
    opcion = input("Selecciona una opción (1-4): ").strip()
    
    if opcion == "1":
        ejecutar_todas_las_busquedas()
    
    elif opcion == "2":
        ejecutar_busqueda_personalizada()
    
    elif opcion == "3":
        scraper = NewsSourcesScraper()
        busqueda = BUSQUEDAS[0]  # Inteligencia Artificial
        resultado = ejecutar_busqueda_individual(scraper, busqueda)
        print(f"\n✅ Búsqueda completada: {resultado['total_hallazgos']} hallazgos encontrados")
    
    elif opcion == "4":
        scraper = NewsSourcesScraper()
        busqueda = BUSQUEDAS[1]  # China y la IA
        resultado = ejecutar_busqueda_individual(scraper, busqueda)
        print(f"\n✅ Búsqueda completada: {resultado['total_hallazgos']} hallazgos encontrados")
    
    else:
        print("❌ Opción no válida")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("✅ Proceso finalizado")
    print("="*70 + "\n")
