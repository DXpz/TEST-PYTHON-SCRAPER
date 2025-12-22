"""
Scraper de Múltiples Fuentes de Noticias
Consulta fuentes específicas y genera JSON con hallazgos
"""

import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time
import re


class NewsSourcesScraper:
    """Scraper especializado para múltiples fuentes de noticias"""
    
    # Fuentes de noticias configuradas
    SOURCES = [
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
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
        })
        self.results = []
    
    def fetch_page(self, url: str, timeout: int = 15) -> Optional[BeautifulSoup]:
        """Obtiene y parsea una página"""
        try:
            print(f"  📄 Accediendo a {urlparse(url).netloc}...")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"  ⚠️  Error: {str(e)[:100]}")
            return None
    
    def extract_articles_generic(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """
        Extrae artículos usando selectores genéricos que funcionan en la mayoría de sitios
        """
        articles = []
        
        # Selectores comunes para artículos
        article_selectors = [
            'article',
            '.article',
            '.post',
            '.entry',
            '.news-item',
            '.story',
            '[class*="article"]',
            '[class*="post"]'
        ]
        
        found_articles = []
        for selector in article_selectors:
            found_articles = soup.select(selector)
            if len(found_articles) > 0:
                break
        
        # Si no encuentra con selectores, busca por tags semánticos
        if not found_articles:
            found_articles = soup.find_all(['article', 'div'], limit=20)
        
        for article in found_articles[:15]:  # Limitar a 15 artículos por fuente
            try:
                # Extraer título
                title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'a'])
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                if len(title) < 10:  # Títulos muy cortos probablemente no sean artículos
                    continue
                
                # Extraer enlace
                link_elem = article.find('a', href=True)
                if not link_elem:
                    link_elem = title_elem if title_elem.name == 'a' else None
                
                link = ''
                if link_elem and link_elem.get('href'):
                    link = link_elem['href']
                    if not link.startswith('http'):
                        link = urljoin(base_url, link)
                
                # Extraer descripción
                description = ''
                desc_elem = article.find('p')
                if desc_elem:
                    description = desc_elem.get_text(strip=True)[:300]
                
                # Extraer imagen
                image = ''
                img_elem = article.find('img')
                if img_elem:
                    image = img_elem.get('src', '') or img_elem.get('data-src', '')
                    if image and not image.startswith('http'):
                        image = urljoin(base_url, image)
                
                # Extraer fecha
                date = ''
                date_elem = article.find(['time', 'span'], class_=lambda x: x and ('date' in str(x).lower() or 'time' in str(x).lower()))
                if date_elem:
                    date = date_elem.get('datetime', '') or date_elem.get_text(strip=True)
                
                articles.append({
                    'titulo': title,
                    'url': link,
                    'descripcion': description,
                    'imagen': image,
                    'fecha': date,
                })
                
            except Exception as e:
                continue
        
        return articles
    
    def filter_by_keywords(self, articles: List[Dict], keywords: List[str]) -> List[Dict]:
        """
        Filtra artículos que contengan palabras clave específicas
        """
        filtered = []
        
        for article in articles:
            text_to_search = f"{article['titulo']} {article['descripcion']}".lower()
            
            # Verificar si contiene alguna palabra clave
            if any(keyword.lower() in text_to_search for keyword in keywords):
                # Calcular relevancia (cuántas keywords coinciden)
                relevance = sum(1 for kw in keywords if kw.lower() in text_to_search)
                article['relevancia'] = relevance
                filtered.append(article)
        
        # Ordenar por relevancia
        filtered.sort(key=lambda x: x.get('relevancia', 0), reverse=True)
        
        return filtered
    
    def scrape_source(self, url: str, keywords: Optional[List[str]] = None) -> Dict:
        """
        Scrapea una fuente específica
        """
        soup = self.fetch_page(url)
        
        if not soup:
            return {
                'fuente': url,
                'nombre_fuente': urlparse(url).netloc,
                'estado': 'error',
                'articulos_encontrados': 0,
                'articulos': []
            }
        
        # Extraer artículos
        articles = self.extract_articles_generic(soup, url)
        
        # Filtrar por palabras clave si se especifican
        if keywords:
            articles = self.filter_by_keywords(articles, keywords)
        
        # Obtener nombre del sitio
        site_name = urlparse(url).netloc.replace('www.', '').split('.')[0].title()
        
        return {
            'fuente': url,
            'nombre_fuente': site_name,
            'estado': 'completado',
            'articulos_encontrados': len(articles),
            'articulos': articles[:10]  # Limitar a top 10
        }
    
    def scrape_all_sources(self, keywords: Optional[List[str]] = None, delay: float = 2.0) -> List[Dict]:
        """
        Scrapea todas las fuentes configuradas
        
        Args:
            keywords: Lista de palabras clave para filtrar (opcional)
            delay: Tiempo de espera entre requests en segundos
            
        Returns:
            Lista de resultados por fuente
        """
        print(f"🕷️  Iniciando scraping de {len(self.SOURCES)} fuentes...")
        if keywords:
            print(f"🔍 Filtrando por: {', '.join(keywords)}\n")
        
        results = []
        
        for i, source_url in enumerate(self.SOURCES, 1):
            print(f"[{i}/{len(self.SOURCES)}] {source_url}")
            
            result = self.scrape_source(source_url, keywords)
            results.append(result)
            
            print(f"  ✓ {result['articulos_encontrados']} artículos encontrados\n")
            
            # Pausa entre requests
            if i < len(self.SOURCES):
                time.sleep(delay)
        
        return results
    
    def generate_search_result(self, search_query: str, keywords: Optional[List[str]] = None) -> Dict:
        """
        Genera un resultado en el formato especificado
        
        Args:
            search_query: Descripción de la búsqueda realizada
            keywords: Palabras clave para filtrar
            
        Returns:
            Diccionario con el formato del resultado
        """
        # Realizar scraping
        sources_results = self.scrape_all_sources(keywords)
        
        # Compilar todos los hallazgos
        all_findings = []
        
        for source in sources_results:
            if source['estado'] == 'completado' and source['articulos_encontrados'] > 0:
                for article in source['articulos']:
                    all_findings.append({
                        'fuente': source['nombre_fuente'],
                        'url_fuente': source['fuente'],
                        'titulo': article['titulo'],
                        'url': article['url'],
                        'descripcion': article['descripcion'],
                        'imagen': article['imagen'],
                        'fecha': article['fecha'],
                        'relevancia': article.get('relevancia', 0)
                    })
        
        # Ordenar por relevancia
        all_findings.sort(key=lambda x: x.get('relevancia', 0), reverse=True)
        
        return {
            'busqueda_realizada': search_query,
            'timestamp': datetime.now().isoformat(),
            'total_fuentes_consultadas': len(self.SOURCES),
            'fuentes_exitosas': sum(1 for s in sources_results if s['estado'] == 'completado'),
            'total_hallazgos': len(all_findings),
            'hallazgos': all_findings,
            'detalle_por_fuente': sources_results
        }
    
    def save_results(self, data: Dict, filename: str = 'news_results.json'):
        """Guarda los resultados en JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Resultados guardados en: {filename}")


def main():
    """Función principal de ejemplo"""
    scraper = NewsSourcesScraper()
    
    print("=" * 60)
    print("   SCRAPER DE NOTICIAS - MÚLTIPLES FUENTES")
    print("=" * 60)
    print()
    
    # Ejemplo 1: Búsqueda sobre IA
    print("📋 Búsqueda 1: Inteligencia Artificial\n")
    
    keywords_ia = [
        'inteligencia artificial',
        'IA',
        'AI',
        'machine learning',
        'deep learning',
        'GPT',
        'LLM',
        'modelo de lenguaje',
        'ChatGPT',
        'OpenAI',
        'Anthropic'
    ]
    
    result_ia = scraper.generate_search_result(
        search_query="Inteligencia Artificial - Últimas Noticias",
        keywords=keywords_ia
    )
    
    # Guardar resultados
    scraper.save_results(result_ia, 'noticias_ia.json')
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    print(f"Búsqueda: {result_ia['busqueda_realizada']}")
    print(f"Fuentes consultadas: {result_ia['total_fuentes_consultadas']}")
    print(f"Fuentes exitosas: {result_ia['fuentes_exitosas']}")
    print(f"Total de hallazgos: {result_ia['total_hallazgos']}")
    
    # Mostrar top 5 hallazgos
    print("\n🏆 TOP 5 ARTICULOS MÁS RELEVANTES:")
    print("-" * 60)
    for i, finding in enumerate(result_ia['hallazgos'][:5], 1):
        print(f"\n{i}. {finding['titulo']}")
        print(f"   Fuente: {finding['fuente']}")
        print(f"   URL: {finding['url'][:80]}...")
        if finding['descripcion']:
            print(f"   {finding['descripcion'][:150]}...")
    
    print("\n" + "=" * 60)
    print("✅ Proceso completado!")
    print("=" * 60)


if __name__ == "__main__":
    main()
