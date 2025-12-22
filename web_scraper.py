"""
Web Scraper - Herramienta para extraer datos de sitios web

Este scraper utiliza requests y BeautifulSoup para extraer información de páginas web.
Incluye funcionalidades para:
- Scraping básico de HTML
- Extracción de enlaces, imágenes y texto
- Manejo de errores
- Exportación a JSON y CSV
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime


class WebScraper:
    """Clase principal para realizar web scraping"""
    
    def __init__(self, base_url: str, headers: Optional[Dict] = None):
        """
        Inicializa el scraper
        
        Args:
            base_url: URL base del sitio web
            headers: Headers HTTP personalizados (opcional)
        """
        self.base_url = base_url
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_page(self, url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
        """
        Obtiene y parsea una página web
        
        Args:
            url: URL de la página a obtener
            timeout: Tiempo máximo de espera en segundos
            
        Returns:
            Objeto BeautifulSoup con el contenido parseado o None si hay error
        """
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener {url}: {e}")
            return None
    
    def extract_links(self, soup: BeautifulSoup, absolute: bool = True) -> List[str]:
        """
        Extrae todos los enlaces de una página
        
        Args:
            soup: Objeto BeautifulSoup
            absolute: Si True, convierte enlaces relativos a absolutos
            
        Returns:
            Lista de URLs
        """
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if absolute:
                href = urljoin(self.base_url, href)
            links.append(href)
        return links
    
    def extract_images(self, soup: BeautifulSoup, absolute: bool = True) -> List[Dict]:
        """
        Extrae todas las imágenes de una página
        
        Args:
            soup: Objeto BeautifulSoup
            absolute: Si True, convierte URLs relativas a absolutas
            
        Returns:
            Lista de diccionarios con información de imágenes
        """
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if absolute and src:
                src = urljoin(self.base_url, src)
            
            images.append({
                'src': src,
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
        return images
    
    def extract_text(self, soup: BeautifulSoup, selector: Optional[str] = None) -> str:
        """
        Extrae texto de una página
        
        Args:
            soup: Objeto BeautifulSoup
            selector: Selector CSS específico (opcional)
            
        Returns:
            Texto extraído
        """
        if selector:
            elements = soup.select(selector)
            return ' '.join([elem.get_text(strip=True) for elem in elements])
        return soup.get_text(strip=True)
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """
        Extrae metadatos de una página
        
        Args:
            soup: Objeto BeautifulSoup
            
        Returns:
            Diccionario con metadatos
        """
        metadata = {
            'title': '',
            'description': '',
            'keywords': '',
            'og_title': '',
            'og_description': '',
            'og_image': ''
        }
        
        # Título
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            property_attr = meta.get('property', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                metadata['description'] = content
            elif name == 'keywords':
                metadata['keywords'] = content
            elif property_attr == 'og:title':
                metadata['og_title'] = content
            elif property_attr == 'og:description':
                metadata['og_description'] = content
            elif property_attr == 'og:image':
                metadata['og_image'] = content
        
        return metadata
    
    def scrape_page(self, url: str) -> Dict:
        """
        Realiza scraping completo de una página
        
        Args:
            url: URL de la página
            
        Returns:
            Diccionario con todos los datos extraídos
        """
        soup = self.fetch_page(url)
        if not soup:
            return {}
        
        return {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'metadata': self.extract_metadata(soup),
            'links': self.extract_links(soup),
            'images': self.extract_images(soup),
            'text_content': self.extract_text(soup)[:500]  # Primeros 500 caracteres
        }
    
    def scrape_multiple(self, urls: List[str], delay: float = 1.0) -> List[Dict]:
        """
        Realiza scraping de múltiples páginas
        
        Args:
            urls: Lista de URLs
            delay: Tiempo de espera entre requests (segundos)
            
        Returns:
            Lista de diccionarios con datos de cada página
        """
        results = []
        for i, url in enumerate(urls):
            print(f"Scraping {i+1}/{len(urls)}: {url}")
            data = self.scrape_page(url)
            if data:
                results.append(data)
            
            # Esperar entre requests para no sobrecargar el servidor
            if i < len(urls) - 1:
                time.sleep(delay)
        
        return results
    
    def save_to_json(self, data: List[Dict], filename: str):
        """
        Guarda los datos en formato JSON
        
        Args:
            data: Datos a guardar
            filename: Nombre del archivo
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ Datos guardados en {filename}")
    
    def save_to_csv(self, data: List[Dict], filename: str):
        """
        Guarda los datos en formato CSV
        
        Args:
            data: Datos a guardar
            filename: Nombre del archivo
        """
        if not data:
            print("No hay datos para guardar")
            return
        
        # Aplanar la estructura para CSV
        flat_data = []
        for item in data:
            flat_item = {
                'url': item.get('url', ''),
                'timestamp': item.get('timestamp', ''),
                'title': item.get('metadata', {}).get('title', ''),
                'description': item.get('metadata', {}).get('description', ''),
                'num_links': len(item.get('links', [])),
                'num_images': len(item.get('images', []))
            }
            flat_data.append(flat_item)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
            writer.writeheader()
            writer.writerows(flat_data)
        print(f"✓ Datos guardados en {filename}")


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo 1: Scraping de una página individual
    print("=== Ejemplo 1: Scraping de una página ===")
    scraper = WebScraper("https://example.com")
    
    # Obtener página
    soup = scraper.fetch_page("https://example.com")
    if soup:
        # Extraer información
        metadata = scraper.extract_metadata(soup)
        print(f"Título: {metadata['title']}")
        
        links = scraper.extract_links(soup)
        print(f"Enlaces encontrados: {len(links)}")
        
        images = scraper.extract_images(soup)
        print(f"Imágenes encontradas: {len(images)}")
    
    print("\n=== Ejemplo 2: Scraping completo con exportación ===")
    # Scraping completo de múltiples URLs
    urls_to_scrape = [
        "https://example.com",
        # Agrega más URLs aquí
    ]
    
    results = scraper.scrape_multiple(urls_to_scrape, delay=1.0)
    
    # Guardar resultados
    if results:
        scraper.save_to_json(results, "scraping_results.json")
        scraper.save_to_csv(results, "scraping_results.csv")
    
    print("\n✓ Scraping completado!")
