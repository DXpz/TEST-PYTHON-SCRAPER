"""
Ejemplo práctico: Scraper de noticias

Este script demuestra cómo usar el WebScraper para extraer noticias
de un sitio web de ejemplo.
"""

from web_scraper import WebScraper
from bs4 import BeautifulSoup
from typing import List, Dict
import json


class NewsScraper(WebScraper):
    """Scraper especializado para noticias"""
    
    def extract_articles(self, soup: BeautifulSoup, article_selector: str) -> List[Dict]:
        """
        Extrae artículos de noticias de una página
        
        Args:
            soup: Objeto BeautifulSoup
            article_selector: Selector CSS para los artículos
            
        Returns:
            Lista de diccionarios con información de cada artículo
        """
        articles = []
        article_elements = soup.select(article_selector)
        
        for article in article_elements:
            # Extraer información del artículo
            title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Buscar enlace
            link_elem = article.find('a', href=True)
            link = link_elem['href'] if link_elem else ''
            if link and not link.startswith('http'):
                link = self.base_url.rstrip('/') + '/' + link.lstrip('/')
            
            # Buscar descripción/extracto
            description_elem = article.find(['p', 'div'], class_=lambda x: x and ('description' in x.lower() or 'excerpt' in x.lower()))
            if not description_elem:
                description_elem = article.find('p')
            description = description_elem.get_text(strip=True) if description_elem else ''
            
            # Buscar imagen
            img_elem = article.find('img')
            image = ''
            if img_elem:
                image = img_elem.get('src', '')
                if image and not image.startswith('http'):
                    image = self.base_url.rstrip('/') + '/' + image.lstrip('/')
            
            # Buscar fecha (común en artículos de noticias)
            date_elem = article.find(['time', 'span'], class_=lambda x: x and 'date' in x.lower())
            date = date_elem.get_text(strip=True) if date_elem else ''
            if not date and date_elem and date_elem.get('datetime'):
                date = date_elem['datetime']
            
            articles.append({
                'title': title,
                'link': link,
                'description': description[:200],  # Primeros 200 caracteres
                'image': image,
                'date': date
            })
        
        return articles
    
    def scrape_news_page(self, url: str, article_selector: str = 'article') -> Dict:
        """
        Scraping especializado para páginas de noticias
        
        Args:
            url: URL de la página de noticias
            article_selector: Selector CSS para artículos
            
        Returns:
            Diccionario con la información de la página
        """
        soup = self.fetch_page(url)
        if not soup:
            return {}
        
        metadata = self.extract_metadata(soup)
        articles = self.extract_articles(soup, article_selector)
        
        return {
            'url': url,
            'page_title': metadata['title'],
            'total_articles': len(articles),
            'articles': articles
        }


def example_quotes_scraper():
    """Ejemplo usando quotes.toscrape.com (sitio de práctica)"""
    print("=== Scraper de Citas ===\n")
    
    scraper = WebScraper("https://quotes.toscrape.com")
    
    # Scrapear la primera página
    soup = scraper.fetch_page("https://quotes.toscrape.com/page/1/")
    
    if soup:
        quotes_data = []
        
        # Extraer todas las citas
        for quote in soup.find_all('div', class_='quote'):
            text = quote.find('span', class_='text').get_text(strip=True)
            author = quote.find('small', class_='author').get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in quote.find_all('a', class_='tag')]
            
            quotes_data.append({
                'quote': text,
                'author': author,
                'tags': tags
            })
        
        # Mostrar resultados
        print(f"✓ Se encontraron {len(quotes_data)} citas\n")
        
        # Mostrar las primeras 3 citas
        for i, quote in enumerate(quotes_data[:3], 1):
            print(f"{i}. {quote['quote']}")
            print(f"   - {quote['author']}")
            print(f"   Tags: {', '.join(quote['tags'])}\n")
        
        # Guardar todas las citas
        with open('quotes.json', 'w', encoding='utf-8') as f:
            json.dump(quotes_data, f, ensure_ascii=False, indent=2)
        
        print("✓ Datos guardados en quotes.json")


def example_news_scraper():
    """Ejemplo de scraper de noticias"""
    print("\n=== Scraper de Noticias (Ejemplo) ===\n")
    
    # Nota: Este es un ejemplo genérico
    # Para un sitio real, necesitas ajustar los selectores
    
    scraper = NewsScraper("https://example-news-site.com")
    
    # Ejemplo de uso (ajusta los selectores según el sitio)
    result = scraper.scrape_news_page(
        "https://example-news-site.com/noticias",
        article_selector="article.news-item"  # Ajusta según el sitio
    )
    
    if result:
        print(f"Página: {result['page_title']}")
        print(f"Artículos encontrados: {result['total_articles']}\n")
        
        # Guardar resultados
        scraper.save_to_json([result], "news_data.json")


def example_custom_scraper():
    """Ejemplo de scraper personalizado para estructura específica"""
    print("\n=== Scraper Personalizado ===\n")
    
    scraper = WebScraper("https://books.toscrape.com")
    soup = scraper.fetch_page("https://books.toscrape.com/")
    
    if soup:
        books = []
        
        # Extraer información de libros
        for book in soup.find_all('article', class_='product_pod'):
            title_elem = book.find('h3').find('a')
            title = title_elem.get('title', '') if title_elem else ''
            
            price_elem = book.find('p', class_='price_color')
            price = price_elem.get_text(strip=True) if price_elem else ''
            
            rating_elem = book.find('p', class_='star-rating')
            rating = rating_elem.get('class', [])[1] if rating_elem else 'N/A'
            
            books.append({
                'title': title,
                'price': price,
                'rating': rating
            })
        
        print(f"✓ Se encontraron {len(books)} libros\n")
        
        # Mostrar los primeros 5
        for i, book in enumerate(books[:5], 1):
            print(f"{i}. {book['title']}")
            print(f"   Precio: {book['price']} | Rating: {book['rating']}\n")
        
        # Guardar datos
        with open('books.json', 'w', encoding='utf-8') as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
        
        print("✓ Datos guardados en books.json")


if __name__ == "__main__":
    print("🕷️  Ejemplos de Web Scraping\n")
    print("=" * 50)
    
    # Ejecutar ejemplo de citas
    example_quotes_scraper()
    
    # Ejecutar ejemplo de libros
    example_custom_scraper()
    
    print("\n" + "=" * 50)
    print("✅ Todos los ejemplos completados!")
    print("\nNota: Para scraping de sitios reales, ajusta los selectores CSS")
    print("según la estructura HTML del sitio objetivo.")
