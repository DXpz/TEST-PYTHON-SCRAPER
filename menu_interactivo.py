"""
Menú interactivo para el scraper de noticias
"""

from news_sources_scraper import NewsSourcesScraper
from datetime import datetime
import os
import sys
from flask import Flask, request, jsonify
import threading


def obtener_banner_red():
    """Retorna las líneas de la parte RED del banner"""
    return [
        " ███████████   ██████████ ██████████",
        "░░███░░░░░███ ░░███░░░░░█░░███░░░░███",
        " ░███    ░███  ░███  █ ░  ░███   ░░███    ",
        " ░██████████   ░██████    ░███    ░███    ",
        " ░███░░░░░███  ░███░░█    ░███    ░███   ",
        " ░███    ░███  ░███ ░   █ ░███    ███   ",
        " █████   █████ ██████████ ███████████  ",
        "░░░░░   ░░░░░ ░░░░░░░░░░ ░░░░░░░░░░░      ",
        "",
        ""
    ]


def obtener_banner_resto():
    """Retorna las líneas del resto del banner"""
    return [
        "                                                                      ",
        "                                                        ░███                    ",
        "  ██████  ████████   ██████   █████   ███   █████ ░███   ██████  ████████ ",
        " ███░░███░░███░░███ ░░░░░░███ ░░███  ░███ ░░███   ░███  ███░░███░░███░░███",
        "░███ ░░░  ░███ ░░░   ███████    ░███ ░███ ░██     ░███ ░███████  ░███ ░░░ ",
        "░███  ███ ░███      ███░░███    ░░███████████     ░███ ░███░░░   ░███     ",
        "░░██████  █████    ░░████████    ░░████░████      █████░░██████  █████    ",
        " ░░░░░░  ░░░░░     ░░░░░░░░░      ░░░░░░░░░       ░░░░░░  ░░░░░░  ░░░░░     ",
        "",
        ""
    ]


def mostrar_banner():
    """Muestra el banner ASCII art con RED en color rojo"""
    # Códigos de color ANSI
    RED = '\033[91m'  # Rojo brillante
    RESET = '\033[0m'  # Resetear color
    
    # Obtener las dos partes del banner
    red_lines = obtener_banner_red()
    resto_lines = obtener_banner_resto()
    
    # Imprimir cada línea con RED en rojo y el resto normal
    for i in range(len(red_lines)):
        red_part = red_lines[i]
        resto_part = resto_lines[i] if i < len(resto_lines) else ""
        
        if red_part or resto_part:
            print(f"{RED}{red_part}{RESET}{resto_part}")
        else:
            print()


def limpiar_pantalla():
    """Limpia la pantalla"""
    os.system('clear' if os.name != 'nt' else 'cls')


def mostrar_menu():
    """Muestra el menú principal"""
    global server_running, server_host, server_port
    
    print("\n" + "=" * 70)
    print("   MENÚ PRINCIPAL")
    print("=" * 70)
    print("\n1. Tema")
    print("2. Fuentes")
    print("3. Servidor API")
    if server_running:
        print(f"   └─ Estado: 🟢 CORRIENDO en http://{server_host}:{server_port}")
    else:
        print("   └─ Estado: 🔴 DETENIDO")
    print("4. Salir")
    print("\n" + "=" * 70)


def opcion_tema(scraper: NewsSourcesScraper):
    """Maneja la opción de búsqueda por tema"""
    limpiar_pantalla()
    mostrar_banner()
    
    print("\n" + "=" * 70)
    print("   BÚSQUEDA POR TEMA")
    print("=" * 70)
    
    tema = input("\n🔍 Ingresa el tema de búsqueda: ").strip()
    
    if not tema:
        print("\n⚠️  No se ingresó ningún tema. Volviendo al menú...")
        input("\nPresiona Enter para continuar...")
        return
    
    # Preguntar por keywords adicionales
    print("\n💡 Palabras clave adicionales (opcional, separadas por comas):")
    keywords_input = input("   Keywords: ").strip()
    
    keywords = None
    if keywords_input:
        keywords = [kw.strip() for kw in keywords_input.split(',') if kw.strip()]
    
    # Si no hay keywords, usar el tema
    if not keywords:
        keywords = [tema]
    else:
        # Añadir el tema a las keywords si no está
        if tema.lower() not in [kw.lower() for kw in keywords]:
            keywords.insert(0, tema)
    
    # Confirmar búsqueda
    print(f"\n📌 Tema: {tema}")
    print(f"📌 Keywords: {', '.join(keywords)}")
    confirmar = input("\n¿Ejecutar búsqueda? (s/n): ").strip().lower()
    
    if confirmar != 's':
        print("\n❌ Búsqueda cancelada.")
        input("\nPresiona Enter para continuar...")
        return
    
    # Ejecutar búsqueda
    limpiar_pantalla()
    mostrar_banner()
    
    print("=" * 70)
    print("   🕷️  SCRAPER DE NOTICIAS MULTI-FUENTE")
    print("=" * 70)
    print(f"\n📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔍 Tema de búsqueda: {tema}")
    print(f"📌 Palabras clave: {', '.join(keywords)}\n")
    
    try:
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
            print(f"\n📰 Top 10 artículos encontrados:\n")
            for i, hallazgo in enumerate(resultado['hallazgos'][:10], 1):
                tipo_icon = '🎯' if hallazgo.get('tipo_match') == 'exacto' else '🔍' if hallazgo.get('tipo_match') == 'similar' else '📌'
                print(f"{i}. {tipo_icon} {hallazgo['titulo']}")
                print(f"   Fuente: {hallazgo['fuente']}")
                print(f"   URL: {hallazgo['url']}")
                if hallazgo.get('contenido'):
                    print(f"   Contenido: {len(hallazgo['contenido'])} caracteres extraídos")
                print()
        
        print(f"\n{'='*70}")
        print("✅ Proceso finalizado")
        print(f"💾 Resultados guardados en: {filename}")
        print(f"{'='*70}\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Búsqueda interrumpida por el usuario.")
    except Exception as e:
        print(f"\n\n❌ Error durante la búsqueda: {str(e)}")
    
    input("\nPresiona Enter para continuar...")


def opcion_fuentes(scraper: NewsSourcesScraper):
    """Maneja la opción de gestión de fuentes"""
    limpiar_pantalla()
    mostrar_banner()
    
    print("\n" + "=" * 70)
    print("   GESTIÓN DE FUENTES")
    print("=" * 70)
    
    print(f"\n📰 Fuentes actuales ({len(scraper.SOURCES)}):\n")
    for i, fuente in enumerate(scraper.SOURCES, 1):
        print(f"  {i}. {fuente}")
    
    print("\n" + "=" * 70)
    print("\nOpciones:")
    print("1. Agregar fuente")
    print("2. Eliminar fuente")
    print("3. Restaurar fuentes por defecto")
    print("4. Volver al menú principal")
    
    opcion = input("\nSelecciona una opción: ").strip()
    
    if opcion == '1':
        nueva_fuente = input("\n🔗 Ingresa la URL de la nueva fuente: ").strip()
        if nueva_fuente:
            if nueva_fuente not in scraper.SOURCES:
                scraper.SOURCES.append(nueva_fuente)
                print(f"\n✅ Fuente agregada: {nueva_fuente}")
            else:
                print(f"\n⚠️  La fuente ya existe en la lista.")
        else:
            print("\n❌ URL inválida.")
    
    elif opcion == '2':
        try:
            indice = int(input(f"\n🔢 Ingresa el número de la fuente a eliminar (1-{len(scraper.SOURCES)}): "))
            if 1 <= indice <= len(scraper.SOURCES):
                fuente_eliminada = scraper.SOURCES.pop(indice - 1)
                print(f"\n✅ Fuente eliminada: {fuente_eliminada}")
            else:
                print("\n❌ Número inválido.")
        except ValueError:
            print("\n❌ Debes ingresar un número válido.")
    
    elif opcion == '3':
        scraper.SOURCES = [
            "https://supplychaindigital.com/",
            "https://www.unesco.org/en",
            "https://www.infobae.com/",
            "https://www.xataka.com/",
            "https://www.genbeta.com/",
            "https://hipertextual.com/",
            "https://techcrunch.com/",
            "https://www.theverge.com/",
            "https://openai.com/es-419/news/",
            "https://www.anthropic.com/engineering",
            "https://deepmind.google/blog/"
        ]
        print("\n✅ Fuentes restauradas a los valores por defecto.")
    
    elif opcion == '4':
        return
    
    else:
        print("\n❌ Opción inválida.")
    
    input("\nPresiona Enter para continuar...")


# Variables globales para el servidor API
api_scraper = None
app = Flask(__name__)
server_thread = None
server_running = False
server_host = None
server_port = None
server_shutdown = None


@app.route('/buscar', methods=['POST'])
def buscar_api():
    """Endpoint API para realizar búsquedas"""
    try:
        data = request.get_json()
        
        if not data or 'tema' not in data:
            return jsonify({
                'error': 'Se requiere el campo "tema" en el JSON',
                'ejemplo': {'tema': 'Inteligencia Artificial', 'keywords': ['IA', 'AI']}
            }), 400
        
        tema = data['tema']
        keywords = data.get('keywords', None)
        
        # Si no hay keywords, usar el tema
        if not keywords:
            keywords = [tema]
        else:
            # Añadir el tema a las keywords si no está
            if tema.lower() not in [kw.lower() for kw in keywords]:
                keywords.insert(0, tema)
        
        # Ejecutar búsqueda usando la lógica existente
        resultado = api_scraper.generate_search_result(
            search_query=tema,
            keywords=keywords
        )
        
        # Guardar resultado (opcional, puedes comentarlo si no quieres guardar)
        filename = f"busqueda_{tema.lower().replace(' ', '_').replace('/', '_')}.json"
        api_scraper.save_results(resultado, filename)
        
        # Retornar resultado en JSON
        return jsonify({
            'success': True,
            'tema': tema,
            'keywords': keywords,
            'resultado': resultado,
            'archivo_guardado': filename
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar que el servidor está funcionando"""
    return jsonify({
        'status': 'ok',
        'servicio': 'Scraper de Noticias API'
    }), 200


@app.route('/', methods=['GET'])
def info():
    """Endpoint de información"""
    return jsonify({
        'servicio': 'Scraper de Noticias API',
        'version': '1.0',
        'endpoints': {
            'POST /buscar': 'Realizar búsqueda por tema',
            'GET /health': 'Verificar estado del servidor'
        },
        'ejemplo_uso': {
            'url': '/buscar',
            'method': 'POST',
            'body': {
                'tema': 'Inteligencia Artificial',
                'keywords': ['IA', 'AI', 'machine learning']
            }
        }
    }), 200


def iniciar_servidor_api(scraper: NewsSourcesScraper, host='0.0.0.0', port=5000):
    """Inicia el servidor API Flask en un hilo"""
    global api_scraper, server_running, server_host, server_port, server_shutdown
    
    api_scraper = scraper
    server_host = host
    server_port = port
    server_running = True
    
    def run_server():
        global server_shutdown
        from werkzeug.serving import make_server
        server = make_server(host, port, app)
        server_shutdown = server.shutdown
        
        print(f"\n{'='*70}")
        print("   🚀 SERVIDOR API INICIADO")
        print(f"{'='*70}")
        print(f"\n📍 Servidor corriendo en: http://{host}:{port}")
        print(f"📡 Endpoint de búsqueda: http://{host}:{port}/buscar")
        print(f"❤️  Health check: http://{host}:{port}/health")
        print(f"\n💡 Ejemplo de uso:")
        print(f"   curl -X POST http://{host}:{port}/buscar \\")
        print(f"        -H 'Content-Type: application/json' \\")
        print(f"        -d '{{\"tema\": \"Inteligencia Artificial\", \"keywords\": [\"IA\", \"AI\"]}}'")
        print(f"\n⚠️  El servidor está corriendo en segundo plano")
        print(f"{'='*70}\n")
        
        server.serve_forever()
    
    # Iniciar servidor en un hilo separado
    global server_thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Dar tiempo para que el servidor inicie
    import time
    time.sleep(1)


def detener_servidor_api():
    """Detiene el servidor API"""
    global server_running, server_thread, server_shutdown
    
    if not server_running:
        return False
    
    try:
        if server_shutdown:
            server_shutdown()
        server_running = False
        server_thread = None
        server_shutdown = None
        return True
    except Exception as e:
        print(f"⚠️  Error al detener el servidor: {str(e)}")
        return False


def opcion_servidor_api(scraper: NewsSourcesScraper):
    """Maneja las opciones del servidor API"""
    global server_running, server_host, server_port
    
    limpiar_pantalla()
    mostrar_banner()
    
    print("\n" + "=" * 70)
    print("   GESTIÓN DEL SERVIDOR API")
    print("=" * 70)
    
    # Mostrar estado actual
    if server_running:
        print(f"\n🟢 Estado: CORRIENDO")
        print(f"📍 URL: http://{server_host}:{server_port}")
        print(f"📡 Endpoint: http://{server_host}:{server_port}/buscar")
    else:
        print("\n🔴 Estado: DETENIDO")
    
    print("\n" + "=" * 70)
    print("\nOpciones:")
    if server_running:
        print("1. Ver información del servidor")
        print("2. Detener servidor")
        print("3. Reiniciar servidor")
        print("4. Volver al menú principal")
    else:
        print("1. Iniciar servidor")
        print("2. Volver al menú principal")
    
    opcion = input("\nSelecciona una opción: ").strip()
    
    if server_running:
        if opcion == '1':
            # Ver información
            limpiar_pantalla()
            mostrar_banner()
            print("\n" + "=" * 70)
            print("   INFORMACIÓN DEL SERVIDOR")
            print("=" * 70)
            print(f"\n🟢 Estado: CORRIENDO")
            print(f"📍 URL base: http://{server_host}:{server_port}")
            print(f"📡 Endpoint de búsqueda: POST http://{server_host}:{server_port}/buscar")
            print(f"❤️  Health check: GET http://{server_host}:{server_port}/health")
            print(f"📋 Información: GET http://{server_host}:{server_port}/")
            print(f"\n💡 Ejemplo de uso con curl:")
            print(f"   curl -X POST http://{server_host}:{server_port}/buscar \\")
            print(f"        -H 'Content-Type: application/json' \\")
            print(f"        -d '{{\"tema\": \"Inteligencia Artificial\"}}'")
            print(f"\n💡 Ejemplo de uso con Python:")
            print(f"   import requests")
            print(f"   response = requests.post('http://{server_host}:{server_port}/buscar',")
            print(f"       json={{\"tema\": \"Inteligencia Artificial\"}})")
            input("\n\nPresiona Enter para continuar...")
        
        elif opcion == '2':
            # Detener servidor
            if detener_servidor_api():
                print("\n✅ Servidor detenido correctamente.")
            else:
                print("\n⚠️  No se pudo detener el servidor o ya estaba detenido.")
            input("\nPresiona Enter para continuar...")
        
        elif opcion == '3':
            # Reiniciar servidor
            print("\n🔄 Reiniciando servidor...")
            detener_servidor_api()
            import time
            time.sleep(1)
            
            limpiar_pantalla()
            mostrar_banner()
            print("\n" + "=" * 70)
            print("   CONFIGURAR SERVIDOR API")
            print("=" * 70)
            print("\n📝 Configuración del servidor:")
            host = input(f"   Host (Enter para {server_host}): ").strip() or server_host
            port_input = input(f"   Puerto (Enter para {server_port}): ").strip() or str(server_port)
            
            try:
                port = int(port_input)
            except ValueError:
                print("\n❌ Puerto inválido. Usando puerto anterior.")
                port = server_port
            
            iniciar_servidor_api(scraper, host, port)
            print("\n✅ Servidor reiniciado correctamente!")
            input("\nPresiona Enter para continuar...")
        
        elif opcion == '4':
            return
    
    else:
        if opcion == '1':
            # Iniciar servidor
            limpiar_pantalla()
            mostrar_banner()
            print("\n" + "=" * 70)
            print("   CONFIGURAR SERVIDOR API")
            print("=" * 70)
            print("\n📝 Configuración del servidor:")
            host = input("   Host (Enter para 0.0.0.0): ").strip() or '0.0.0.0'
            port_input = input("   Puerto (Enter para 5000): ").strip() or '5000'
            
            try:
                port = int(port_input)
            except ValueError:
                print("\n❌ Puerto inválido. Usando puerto 5000 por defecto.")
                port = 5000
            
            print(f"\n✅ Iniciando servidor en {host}:{port}...")
            iniciar_servidor_api(scraper, host, port)
            print("\n✅ Servidor iniciado correctamente!")
            print("   Puedes continuar usando el menú o hacer requests HTTP al servidor.")
            input("\nPresiona Enter para continuar...")
        
        elif opcion == '2':
            return


def main():
    """Función principal del menú interactivo"""
    scraper = NewsSourcesScraper()
    
    while True:
        limpiar_pantalla()
        mostrar_banner()
        mostrar_menu()
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == '1':
            opcion_tema(scraper)
        elif opcion == '2':
            opcion_fuentes(scraper)
        elif opcion == '3':
            opcion_servidor_api(scraper)
        elif opcion == '4':
            # Detener servidor si está corriendo antes de salir
            if server_running:
                print("\n⚠️  Deteniendo servidor API...")
                detener_servidor_api()
            limpiar_pantalla()
            print("\n👋 ¡Hasta luego!\n")
            sys.exit(0)
        else:
            print("\n❌ Opción inválida. Por favor selecciona 1, 2, 3 o 4.")
            input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!\n")
        sys.exit(0)

