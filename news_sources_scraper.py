"""
Scraper de Múltiples Fuentes de Noticias
Consulta fuentes específicas y genera JSON con hallazgos

NOTA LEGAL IMPORTANTE:
- Este scraper verifica robots.txt antes de acceder a cada sitio
- El contenido scrapeado debe usarse respetando los derechos de autor
- Si el contenido se usa para generar noticias con IA, asegúrate de:
  * Citar las fuentes originales
  * No reproducir contenido completo sin permiso
  * Respetar los términos de servicio de cada sitio
  * Considerar el uso justo (fair use) según tu jurisdicción
"""

import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time
import re
import random
import os
from urllib.robotparser import RobotFileParser


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
        # User-Agent identificable del bot (mejor práctica ética)
        self.user_agent = 'NewsScraperBot/1.0 (+https://github.com/DXpz/TEST-PYTHON-SCRAPER)'
        # Headers más completos para evitar bloqueos
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/'
        })
        self.results = []
        self.robots_cache = {}  # Cache para robots.txt
    
    def check_robots_txt(self, url: str) -> bool:
        """
        Verifica si el scraper puede acceder a una URL según robots.txt
        Retorna True si está permitido, False si está bloqueado
        """
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            robots_url = urljoin(base_url, '/robots.txt')
            
            # Usar cache si ya verificamos este dominio
            if base_url in self.robots_cache:
                rp = self.robots_cache[base_url]
            else:
                rp = RobotFileParser()
                rp.set_url(robots_url)
                rp.read()
                self.robots_cache[base_url] = rp
            
            # Verificar si nuestro User-Agent puede acceder
            can_fetch = rp.can_fetch(self.user_agent, url)
            
            if not can_fetch:
                print(f"  🚫 robots.txt bloquea el acceso a esta URL")
            
            return can_fetch
            
        except Exception as e:
            # Si hay error al leer robots.txt, asumir que está permitido
            # (muchos sitios no tienen robots.txt o no es accesible)
            print(f"  ℹ️  No se pudo verificar robots.txt: {str(e)[:50]}")
            return True  # Permitir por defecto si no se puede verificar
    
    def fetch_page(self, url: str, timeout: int = 20, check_robots: bool = True) -> Optional[BeautifulSoup]:
        """Obtiene y parsea una página con mejor manejo de errores"""
        try:
            # Verificar robots.txt antes de acceder
            if check_robots:
                if not self.check_robots_txt(url):
                    return None
            
            print(f"  📄 Accediendo a {urlparse(url).netloc}...")
            # Agregar delay aleatorio para parecer más humano
            time.sleep(random.uniform(1, 3))
            
            # Actualizar referer con la URL actual
            headers = self.session.headers.copy()
            headers['Referer'] = urlparse(url).scheme + '://' + urlparse(url).netloc
            
            response = self.session.get(url, timeout=timeout, headers=headers, allow_redirects=True)
            response.raise_for_status()
            
            # Verificar que realmente recibimos contenido HTML
            if not response.content or len(response.content) < 100:
                print(f"  ⚠️  Respuesta vacía o muy corta")
                return None
                
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.ConnectionError as e:
            print(f"  ⚠️  Error de conexión (posible bloqueo): {str(e)[:100]}")
            return None
        except requests.exceptions.Timeout:
            print(f"  ⚠️  Timeout esperando respuesta")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"  ⚠️  Error HTTP {e.response.status_code if hasattr(e, 'response') else 'desconocido'}")
            return None
        except Exception as e:
            print(f"  ⚠️  Error: {str(e)[:100]}")
            return None
    
    def extract_articles_generic(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """
        Extrae artículos usando selectores genéricos mejorados que funcionan en la mayoría de sitios
        """
        articles = []
        seen_urls = set()  # Para evitar duplicados
        
        # Selectores mejorados y más completos para artículos
        article_selectors = [
            'article',
            '.article',
            '.post',
            '.entry',
            '.news-item',
            '.story',
            '.card',
            '.item',
            '[class*="article"]',
            '[class*="post"]',
            '[class*="card"]',
            '[class*="item"]',
            '[class*="news"]',
            '[class*="story"]',
            '[class*="entry"]',
            'li[class*="article"]',
            'li[class*="post"]',
            'div[class*="article"]',
            'div[class*="post"]',
            'section article',
            'main article',
            '.content article',
            '.main article'
        ]
        
        found_articles = []
        for selector in article_selectors:
            try:
                found = soup.select(selector)
                if len(found) > 0:
                    found_articles.extend(found)
            except:
                continue
        
        # Si no encuentra con selectores, busca por tags semánticos y estructura
        if not found_articles:
            # Buscar en listas
            found_articles = soup.find_all(['article', 'li'], limit=30)
            if len(found_articles) < 5:
                # Buscar divs con estructura de artículo
                found_articles = soup.find_all('div', class_=lambda x: x and any(
                    keyword in str(x).lower() for keyword in ['article', 'post', 'card', 'item', 'news', 'story']
                ), limit=30)
        
        # También buscar todos los enlaces que parezcan artículos
        all_links = soup.find_all('a', href=True)
        article_links = []
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            # Filtrar enlaces que parezcan artículos (tienen texto significativo y URL válida)
            if (len(text) > 15 and 
                href and 
                not any(skip in href.lower() for skip in ['#', 'javascript:', 'mailto:', 'tel:', '/tag/', '/category/', '/author/']) and
                (href.startswith('http') or href.startswith('/'))):
                article_links.append(link)
        
        # Procesar artículos encontrados
        for article in found_articles[:20]:  # Aumentar límite a 20
            try:
                # Extraer título - múltiples estrategias
                title = ''
                title_elem = None
                
                # Estrategia 1: Buscar en headers dentro del artículo
                for tag in ['h1', 'h2', 'h3', 'h4', 'h5']:
                    title_elem = article.find(tag)
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        if len(title) >= 10:
                            break
                
                # Estrategia 2: Buscar en enlaces
                if not title or len(title) < 10:
                    link_elem = article.find('a', href=True)
                    if link_elem:
                        title = link_elem.get_text(strip=True)
                        title_elem = link_elem
                
                # Estrategia 3: Buscar en atributos data o aria
                if not title or len(title) < 10:
                    title = (article.get('data-title') or 
                            article.get('aria-label') or 
                            article.get('title', '')).strip()
                
                if not title or len(title) < 10:
                    continue
                
                # Extraer enlace - múltiples estrategias
                link = ''
                link_elem = article.find('a', href=True)
                
                if link_elem:
                    link = link_elem.get('href', '')
                elif title_elem and title_elem.name == 'a':
                    link = title_elem.get('href', '')
                elif article.name == 'a':
                    link = article.get('href', '')
                
                # Normalizar URL
                if link:
                    if not link.startswith('http'):
                        link = urljoin(base_url, link)
                    # Evitar duplicados
                    if link in seen_urls:
                        continue
                    seen_urls.add(link)
                else:
                    continue
                
                # Extraer descripción - múltiples estrategias
                description = ''
                # Buscar en párrafos
                for p in article.find_all(['p', 'div'], limit=3):
                    text = p.get_text(strip=True)
                    if len(text) > 30 and len(text) < 500:
                        description = text[:300]
                        break
                
                # Si no hay descripción, buscar en atributos
                if not description:
                    description = (article.get('data-description') or 
                                 article.get('data-summary') or '').strip()[:300]
                
                # Extraer imagen - múltiples estrategias
                image = ''
                img_elem = article.find('img')
                if img_elem:
                    image = (img_elem.get('src') or 
                            img_elem.get('data-src') or 
                            img_elem.get('data-lazy-src') or
                            img_elem.get('data-original') or '')
                    if image and not image.startswith('http'):
                        image = urljoin(base_url, image)
                
                # Extraer fecha - múltiples estrategias
                date = ''
                # Buscar en time tag
                date_elem = article.find('time')
                if date_elem:
                    date = date_elem.get('datetime', '') or date_elem.get_text(strip=True)
                
                # Buscar en spans/divs con clases de fecha
                if not date:
                    date_elems = article.find_all(['time', 'span', 'div'], 
                                                  class_=lambda x: x and any(
                                                      keyword in str(x).lower() 
                                                      for keyword in ['date', 'time', 'published', 'updated']
                                                  ))
                    for de in date_elems:
                        date = de.get('datetime', '') or de.get_text(strip=True)
                        if date:
                            break
                
                articles.append({
                    'titulo': title,
                    'url': link,
                    'descripcion': description,
                    'imagen': image,
                    'fecha': date,
                })
                
            except Exception as e:
                continue
        
        # Procesar enlaces adicionales que parezcan artículos
        for link_elem in article_links[:15]:
            try:
                href = link_elem.get('href', '')
                if not href.startswith('http'):
                    href = urljoin(base_url, href)
                
                if href in seen_urls:
                    continue
                seen_urls.add(href)
                
                title = link_elem.get_text(strip=True)
                if len(title) >= 10:
                    articles.append({
                        'titulo': title,
                        'url': href,
                        'descripcion': '',
                        'imagen': '',
                        'fecha': '',
                    })
            except:
                continue
        
        return articles
    
    def extract_article_content(self, url: str) -> str:
        """
        Extrae el contenido completo de un artículo visitando su URL
        """
        try:
            soup = self.fetch_page(url)
            if not soup:
                return ""
            
            # Selectores comunes para el contenido del artículo
            content_selectors = [
                'article',
                '.article-content',
                '.post-content',
                '.entry-content',
                '.article-body',
                '.content',
                '[class*="article-content"]',
                '[class*="post-content"]',
                '[class*="entry-content"]',
                'main article',
                '.main-content article'
            ]
            
            content_text = ""
            
            # Intentar con selectores específicos
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remover scripts, estilos y otros elementos no deseados
                    for script in content_elem(["script", "style", "nav", "aside", "footer", "header", "iframe"]):
                        script.decompose()
                    
                    # Extraer todos los párrafos
                    paragraphs = content_elem.find_all(['p', 'div'])
                    content_parts = []
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and len(text) > 20:  # Filtrar textos muy cortos
                            content_parts.append(text)
                    
                    if content_parts:
                        content_text = "\n\n".join(content_parts)
                        break
            
            # Si no se encontró con selectores específicos, intentar extraer de body
            if not content_text:
                body = soup.find('body')
                if body:
                    # Remover elementos no deseados
                    for script in body(["script", "style", "nav", "aside", "footer", "header", "iframe", "noscript"]):
                        script.decompose()
                    
                    # Buscar el contenido principal
                    main_content = body.find(['main', 'article', 'div'], class_=lambda x: x and ('content' in str(x).lower() or 'article' in str(x).lower() or 'post' in str(x).lower()))
                    if main_content:
                        paragraphs = main_content.find_all(['p', 'div'])
                        content_parts = []
                        for p in paragraphs:
                            text = p.get_text(strip=True)
                            if text and len(text) > 20:
                                content_parts.append(text)
                        if content_parts:
                            content_text = "\n\n".join(content_parts)
            
            return content_text[:10000]  # Limitar a 10000 caracteres
            
        except Exception as e:
            print(f"  ⚠️  Error extrayendo contenido de {url}: {str(e)[:100]}")
            return ""
    
    def calculate_similarity(self, text: str, keywords: List[str], tema: str) -> float:
        """
        Calcula la similitud mejorada de un texto con el tema y keywords
        Retorna un score de 0 a 100
        """
        text_lower = text.lower()
        tema_lower = tema.lower()
        
        # Normalizar texto (remover caracteres especiales para mejor matching)
        text_normalized = re.sub(r'[^\w\s]', ' ', text_lower)
        tema_normalized = re.sub(r'[^\w\s]', ' ', tema_lower)
        
        # Dividir tema en palabras significativas (más de 3 caracteres)
        tema_words = [w for w in tema_normalized.split() if len(w) > 3]
        
        score = 0.0
        
        # Coincidencia exacta de keywords completas (peso muy alto)
        for kw in keywords:
            kw_lower = kw.lower()
            kw_normalized = re.sub(r'[^\w\s]', ' ', kw_lower)
            
            # Coincidencia exacta de la keyword completa
            if kw_normalized in text_normalized:
                # Puntuación basada en longitud de keyword (keywords más largas = más específicas)
                base_score = 15 + len(kw_normalized) * 3
                score += base_score
            
            # Coincidencia de todas las palabras de la keyword
            kw_words = [w for w in kw_normalized.split() if len(w) > 2]
            if len(kw_words) > 1:
                matches = sum(1 for word in kw_words if word in text_normalized)
                if matches == len(kw_words):  # Todas las palabras coinciden
                    score += 12
                elif matches > len(kw_words) * 0.7:  # Más del 70% de palabras
                    score += 8
        
        # Coincidencia de palabras del tema (peso medio)
        for word in tema_words:
            if word in text_normalized:
                score += 6
        
        # Coincidencias parciales de palabras individuales (peso bajo)
        all_keywords_words = []
        for kw in keywords:
            kw_normalized = re.sub(r'[^\w\s]', ' ', kw.lower())
            all_keywords_words.extend([w for w in kw_normalized.split() if len(w) > 3])
        
        for kw_word in set(all_keywords_words):  # Usar set para evitar duplicados
            if kw_word in text_normalized:
                score += 3
        
        # Bonus por coincidencia en el título (si el texto parece ser un título)
        if len(text) < 200:  # Probablemente es un título
            for kw in keywords:
                if kw.lower() in text_lower:
                    score += 5
        
        return min(score, 200)  # Limitar score máximo pero permitir valores altos
    
    def filter_by_keywords(self, articles: List[Dict], keywords: List[str], tema: str = "", min_results: int = 5) -> List[Dict]:
        """
        Filtra artículos que contengan palabras clave específicas o sean similares al tema
        Si no encuentra suficientes resultados exactos, usa similitud flexible
        """
        filtered_exact = []
        filtered_similar = []
        
        for article in articles:
            text_to_search = f"{article['titulo']} {article['descripcion']}".lower()
            
            # Verificar coincidencia exacta con keywords
            exact_match = any(keyword.lower() in text_to_search for keyword in keywords)
            
            if exact_match:
                # Calcular relevancia (cuántas keywords coinciden)
                relevance = sum(1 for kw in keywords if kw.lower() in text_to_search)
                article['relevancia'] = relevance + 100  # Bonus por coincidencia exacta
                filtered_exact.append(article)
            else:
                # Calcular similitud si hay tema
                if tema:
                    similarity_score = self.calculate_similarity(
                        f"{article['titulo']} {article['descripcion']}",
                        keywords,
                        tema
                    )
                    if similarity_score > 0:
                        article['relevancia'] = similarity_score
                        article['tipo_match'] = 'similar'
                        filtered_similar.append(article)
        
        # Si hay suficientes resultados exactos, usar solo esos
        if len(filtered_exact) >= min_results:
            filtered_exact.sort(key=lambda x: x.get('relevancia', 0), reverse=True)
            for article in filtered_exact:
                article['tipo_match'] = 'exacto'
            return filtered_exact
        
        # Si no hay suficientes exactos, combinar con similares
        all_filtered = filtered_exact + filtered_similar
        all_filtered.sort(key=lambda x: x.get('relevancia', 0), reverse=True)
        
        # Marcar tipo de match
        for article in filtered_exact:
            article['tipo_match'] = 'exacto'
        
        # Si aún no hay suficientes, tomar los mejores de todos los artículos
        if len(all_filtered) < min_results:
            # Calcular similitud para todos los artículos restantes
            remaining_articles = [a for a in articles if a not in all_filtered]
            for article in remaining_articles:
                if tema:
                    similarity_score = self.calculate_similarity(
                        f"{article['titulo']} {article['descripcion']}",
                        keywords,
                        tema
                    )
                    if similarity_score > 0:  # Solo agregar si tiene alguna similitud
                        article['relevancia'] = similarity_score
                        article['tipo_match'] = 'flexible'
                        all_filtered.append(article)
            
            all_filtered.sort(key=lambda x: x.get('relevancia', 0), reverse=True)
        
        # Si aún no hay resultados, devolver los primeros artículos disponibles
        if len(all_filtered) == 0:
            print(f"  ⚠️  No se encontraron artículos similares, devolviendo artículos disponibles...")
            for i, article in enumerate(articles[:min_results]):
                article['relevancia'] = 1
                article['tipo_match'] = 'sin_filtro'
                all_filtered.append(article)
        
        return all_filtered
    
    def get_search_url(self, base_url: str, query: str) -> Optional[str]:
        """
        Intenta generar una URL de búsqueda para una fuente
        """
        query_encoded = requests.utils.quote(query)
        domain = urlparse(base_url).netloc.lower()
        
        # Patrones comunes de URLs de búsqueda
        search_patterns = [
            f"{base_url}search?q={query_encoded}",
            f"{base_url}search/?q={query_encoded}",
            f"{base_url}?s={query_encoded}",
            f"{base_url}?search={query_encoded}",
            f"{base_url}buscar?q={query_encoded}",
            f"{base_url}buscar/?q={query_encoded}",
        ]
        
        # Patrones específicos por dominio
        if 'xataka' in domain or 'genbeta' in domain:
            search_patterns.insert(0, f"{base_url}?s={query_encoded}")
        elif 'infobae' in domain:
            search_patterns.insert(0, f"{base_url}buscar?q={query_encoded}")
        elif 'techcrunch' in domain or 'theverge' in domain:
            search_patterns.insert(0, f"{base_url}search?q={query_encoded}")
        
        return search_patterns[0] if search_patterns else None
    
    def scrape_source(self, url: str, keywords: Optional[List[str]] = None, tema: str = "") -> Dict:
        """
        Scrapea una fuente específica con estrategias mejoradas
        """
        all_articles = []
        
        # Estrategia 1: Scrapear la página principal
        soup = self.fetch_page(url)
        
        if soup:
            articles = self.extract_articles_generic(soup, url)
            all_articles.extend(articles)
        
        # Estrategia 2: Si hay tema/keywords, intentar buscar en URL de búsqueda
        if (keywords or tema) and len(all_articles) < 10:
            search_query = tema if tema else ' '.join(keywords[:2]) if keywords else ''
            if search_query:
                search_url = self.get_search_url(url, search_query)
                if search_url and search_url != url:
                    print(f"  🔍 Intentando búsqueda en: {urlparse(search_url).netloc}...")
                    search_soup = self.fetch_page(search_url)
                    if search_soup:
                        search_articles = self.extract_articles_generic(search_soup, search_url)
                        # Evitar duplicados
                        existing_urls = {a['url'] for a in all_articles}
                        for article in search_articles:
                            if article['url'] not in existing_urls:
                                all_articles.append(article)
                                existing_urls.add(article['url'])
        
        if not all_articles:
            return {
                'fuente': url,
                'nombre_fuente': urlparse(url).netloc,
                'estado': 'error',
                'articulos_encontrados': 0,
                'articulos': []
            }
        
        # Filtrar por palabras clave si se especifican, usando filtro flexible
        if keywords or tema:
            all_articles = self.filter_by_keywords(all_articles, keywords or [], tema)
        
        # Obtener nombre del sitio
        site_name = urlparse(url).netloc.replace('www.', '').split('.')[0].title()
        
        return {
            'fuente': url,
            'nombre_fuente': site_name,
            'estado': 'completado',
            'articulos_encontrados': len(all_articles),
            'articulos': all_articles[:15]  # Aumentar a top 15
        }
    
    def scrape_all_sources(self, keywords: Optional[List[str]] = None, tema: str = "", delay: float = 3.0) -> List[Dict]:
        """
        Scrapea todas las fuentes configuradas
        
        Args:
            keywords: Lista de palabras clave para filtrar (opcional)
            tema: Tema de búsqueda para filtro flexible
            delay: Tiempo de espera entre requests en segundos
            
        Returns:
            Lista de resultados por fuente
        """
        print(f"🕷️  Iniciando scraping de {len(self.SOURCES)} fuentes...")
        print(f"🤖 User-Agent: {self.user_agent}")
        print(f"📋 Verificando robots.txt antes de cada acceso...")
        if keywords:
            print(f"🔍 Filtrando por: {', '.join(keywords)}")
        if tema:
            print(f"📌 Tema: {tema}")
        print()
        
        results = []
        
        for i, source_url in enumerate(self.SOURCES, 1):
            print(f"[{i}/{len(self.SOURCES)}] {source_url}")
            
            result = self.scrape_source(source_url, keywords, tema)
            results.append(result)
            
            print(f"  ✓ {result['articulos_encontrados']} artículos encontrados\n")
            
            # Pausa entre requests (con variación aleatoria para parecer más humano)
            if i < len(self.SOURCES):
                time.sleep(delay + random.uniform(0.5, 1.5))
        
        return results
    
    def generate_search_result(self, search_query: str, keywords: Optional[List[str]] = None) -> Dict:
        """
        Genera un resultado en el formato especificado
        
        Args:
            search_query: Descripción de la búsqueda realizada (tema)
            keywords: Palabras clave para filtrar
            
        Returns:
            Diccionario con el formato del resultado
        """
        # Advertencia sobre uso del contenido
        print("\n" + "="*70)
        print("⚠️  ADVERTENCIA LEGAL")
        print("="*70)
        print("El contenido obtenido debe usarse respetando:")
        print("  • Derechos de autor de las fuentes originales")
        print("  • Términos de servicio de cada sitio")
        print("  • Si se usa para generar noticias con IA:")
        print("    - Citar siempre las fuentes originales")
        print("    - No reproducir contenido completo sin permiso")
        print("    - Considerar el uso justo (fair use)")
        print("="*70 + "\n")
        
        # Realizar scraping con filtro flexible usando el tema
        sources_results = self.scrape_all_sources(keywords, tema=search_query)
        
        # Compilar todos los hallazgos
        all_findings = []
        total_articulos = sum(len(s['articulos']) for s in sources_results if s['estado'] == 'completado')
        
        # Contar tipos de match
        exactos = 0
        similares = 0
        flexibles = 0
        
        if total_articulos > 0:
            print(f"\n📄 Extrayendo contenido completo de {total_articulos} artículos...")
            
            for source in sources_results:
                if source['estado'] == 'completado' and source['articulos_encontrados'] > 0:
                    for i, article in enumerate(source['articulos'], 1):
                        tipo_match = article.get('tipo_match', 'exacto')
                        match_icon = '🎯' if tipo_match == 'exacto' else '🔍' if tipo_match == 'similar' else '📌' if tipo_match == 'flexible' else '📄'
                        print(f"  [{i}/{len(source['articulos'])}] {match_icon} Extrayendo: {article['titulo'][:60]}...")
                        
                        # Contar tipos
                        if tipo_match == 'exacto':
                            exactos += 1
                        elif tipo_match == 'similar':
                            similares += 1
                        elif tipo_match == 'flexible':
                            flexibles += 1
                        
                        # Extraer contenido completo del artículo
                        contenido_completo = ""
                        if article.get('url'):
                            contenido_completo = self.extract_article_content(article['url'])
                            time.sleep(1)  # Pausa entre extracciones de contenido
                        
                        all_findings.append({
                            'fuente': source['nombre_fuente'],
                            'url_fuente': source['fuente'],
                            'titulo': article['titulo'],
                            'url': article['url'],
                            'descripcion': article['descripcion'],
                            'contenido': contenido_completo,
                            'imagen': article['imagen'],
                            'fecha': article['fecha'],
                            'relevancia': article.get('relevancia', 0),
                            'tipo_match': tipo_match,
                            # Información adicional para facilitar citación en IA
                            'cita_formato': f"{source['nombre_fuente']} - {article['titulo']} ({article['url']})",
                            'cita_corta': f"{source['nombre_fuente']}"
                        })
            
            # Mostrar resumen de tipos de match
            if similares > 0 or flexibles > 0:
                print(f"\n📊 Resumen de coincidencias:")
                if exactos > 0:
                    print(f"   🎯 Exactos: {exactos}")
                if similares > 0:
                    print(f"   🔍 Similares: {similares}")
                if flexibles > 0:
                    print(f"   📌 Flexibles: {flexibles}")
        
        # Ordenar por relevancia
        all_findings.sort(key=lambda x: x.get('relevancia', 0), reverse=True)
        
        # Agrupar por fuente para análisis periodístico
        fuentes_unicas = {}
        for hallazgo in all_findings:
            fuente_nombre = hallazgo['fuente']
            if fuente_nombre not in fuentes_unicas:
                fuentes_unicas[fuente_nombre] = {
                    'nombre': fuente_nombre,
                    'url_base': hallazgo['url_fuente'],
                    'total_articulos': 0,
                    'articulos': []
                }
            fuentes_unicas[fuente_nombre]['total_articulos'] += 1
            fuentes_unicas[fuente_nombre]['articulos'].append({
                'titulo': hallazgo['titulo'],
                'url': hallazgo['url'],
                'fecha': hallazgo['fecha']
            })
        
        # Crear resumen periodístico
        resumen_periodistico = {
            'tema_principal': search_query,
            'total_fuentes_consultadas': len(self.SOURCES),
            'fuentes_exitosas': sum(1 for s in sources_results if s['estado'] == 'completado'),
            'total_articulos': len(all_findings),
            'fuentes_unicas': len(fuentes_unicas),
            'cobertura_temporal': {
                'mas_reciente': max([h['fecha'] for h in all_findings if h['fecha']], default=''),
                'mas_antigua': min([h['fecha'] for h in all_findings if h['fecha']], default='')
            },
            'perspectivas': list(fuentes_unicas.keys())  # Diferentes perspectivas/medios
        }
        
        return {
            'busqueda_realizada': search_query,
            'timestamp': datetime.now().isoformat(),
            'resumen_periodistico': resumen_periodistico,
            'total_fuentes_consultadas': len(self.SOURCES),
            'fuentes_exitosas': sum(1 for s in sources_results if s['estado'] == 'completado'),
            'total_hallazgos': len(all_findings),
            'hallazgos': all_findings,
            'fuentes_agrupadas': list(fuentes_unicas.values()),  # Agrupado por fuente para análisis
            'detalle_por_fuente': sources_results,
            'advertencia_legal': {
                'mensaje': 'Este contenido debe usarse respetando derechos de autor y términos de servicio',
                'uso_ia': 'Si se usa para generar noticias con IA, siempre citar las fuentes originales',
                'fuentes': [s['fuente'] for s in sources_results if s['estado'] == 'completado']
            },
            'nota_para_periodista_ia': {
                'instrucciones': 'Usa esta información para escribir un artículo periodístico profesional',
                'verificacion_cruzada': f'Consulta múltiples fuentes ({len(fuentes_unicas)} fuentes únicas disponibles)',
                'citacion': 'Cita siempre las fuentes originales usando los campos "cita_formato" o "cita_corta"',
                'contexto_temporal': f'Artículos desde {resumen_periodistico["cobertura_temporal"]["mas_antigua"]} hasta {resumen_periodistico["cobertura_temporal"]["mas_reciente"]}',
                'perspectivas_disponibles': resumen_periodistico['perspectivas']
            }
        }
    
    def save_results(self, data: Dict, filename: str = 'news_results.json'):
        """Guarda los resultados en JSON en la carpeta 'resultados'"""
        # Crear carpeta resultados si no existe
        resultados_dir = 'resultados'
        if not os.path.exists(resultados_dir):
            os.makedirs(resultados_dir)
        
        # Guardar en la carpeta resultados
        filepath = os.path.join(resultados_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Resultados guardados en: {filepath}")
