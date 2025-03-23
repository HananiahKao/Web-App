import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def validate_url(url):
    """
    Validate if the provided string is a proper URL
    
    Args:
        url (str): URL to validate
    
    Returns:
        bool: True if URL is valid, False otherwise
    """
    # Add http:// prefix if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def scrape_website(url, elements):
    """
    Scrape website for specified elements
    
    Args:
        url (str): URL to scrape
        elements (list): List of elements to extract (links, headings, paragraphs, etc.)
    
    Returns:
        dict: Dictionary with extracted elements
    """
    # Add http:// prefix if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    logger.debug(f"Scraping URL: {url}")
    logger.debug(f"Elements to extract: {elements}")
    
    try:
        # Set user-agent header to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Send HTTP request
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract elements based on user selection
        results = {}
        
        if 'links' in elements:
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text(strip=True) or "[No text]"
                if href:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        parsed_url = urlparse(url)
                        href = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"
                    links.append({'url': href, 'text': text})
            results['links'] = links
        
        if 'headings' in elements:
            headings = []
            for heading_level in range(1, 7):
                for heading in soup.find_all(f'h{heading_level}'):
                    text = heading.get_text(strip=True)
                    if text:
                        headings.append({'level': heading_level, 'text': text})
            results['headings'] = headings
        
        if 'paragraphs' in elements:
            paragraphs = []
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if text:
                    paragraphs.append(text)
            results['paragraphs'] = paragraphs
        
        if 'images' in elements:
            images = []
            for img in soup.find_all('img'):
                src = img.get('src')
                alt = img.get('alt', '')
                if src:
                    # Convert relative URLs to absolute
                    if src.startswith('/'):
                        parsed_url = urlparse(url)
                        src = f"{parsed_url.scheme}://{parsed_url.netloc}{src}"
                    images.append({'src': src, 'alt': alt})
            results['images'] = images
        
        if 'meta' in elements:
            meta_tags = []
            for meta in soup.find_all('meta'):
                properties = {}
                for attr in meta.attrs:
                    properties[attr] = meta.get(attr)
                if properties:
                    meta_tags.append(properties)
            results['meta'] = meta_tags
        
        if 'tables' in elements:
            tables = []
            for table in soup.find_all('table'):
                rows = []
                for tr in table.find_all('tr'):
                    row = []
                    for td in tr.find_all(['td', 'th']):
                        row.append(td.get_text(strip=True))
                    if row:
                        rows.append(row)
                if rows:
                    tables.append(rows)
            results['tables'] = tables
        
        if 'forms' in elements:
            forms = []
            for form in soup.find_all('form'):
                form_data = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get'),
                    'inputs': []
                }
                
                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    input_data = {
                        'type': input_tag.name if input_tag.name in ['textarea', 'select'] else input_tag.get('type', 'text'),
                        'name': input_tag.get('name', ''),
                        'id': input_tag.get('id', '')
                    }
                    form_data['inputs'].append(input_data)
                
                forms.append(form_data)
            results['forms'] = forms
        
        if 'scripts' in elements:
            scripts = []
            for script in soup.find_all('script', src=True):
                src = script.get('src')
                if src:
                    # Convert relative URLs to absolute
                    if src.startswith('/'):
                        parsed_url = urlparse(url)
                        src = f"{parsed_url.scheme}://{parsed_url.netloc}{src}"
                    scripts.append(src)
            results['scripts'] = scripts
        
        if 'full_html' in elements:
            results['full_html'] = str(soup)
        
        return results
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise Exception(f"Failed to fetch the website: {str(e)}")
    
    except Exception as e:
        logger.error(f"Scraping error: {str(e)}")
        raise Exception(f"Error scraping the website: {str(e)}")
