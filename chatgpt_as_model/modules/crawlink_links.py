from urllib.parse import urljoin, urlparse, urlunparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time
from bs4 import BeautifulSoup
from logs import get_logger

logger = get_logger("debug_logger","logs/debug/debug_logger.log")
logger_error = get_logger("error_logger","logs/error/error_logger.log")


def normalize_url(url):
    """Strip URL to base, removing query params and fragments."""
    try:
        parsed_url = urlparse(url)
        return urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    except Exception as e:
        logger_error.error(f"Normalize URL Function Failed line21 file crawling_links : {str(e)}")

def fetch_url(current_url, base_netloc, visited, failed_links, max_retries=3):
    """Fetch the URL and return the normalized URL and found links. Retry on failure."""
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(current_url, timeout=5, stream=True)
            response.raise_for_status()

            # Check for content type and categorize accordingly
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                # Classify non-HTML content types
                if 'application/pdf' in content_type:
                    # print(f"Found PDF content: {current_url}")
                    return current_url, [], 'pdf'
                elif 'application/zip' in content_type:
                    # print(f"Found ZIP content: {current_url}")
                    return current_url, [], 'zip'
                else:
                    # print(f"Found other non-HTML content: {current_url} (Content-Type: {content_type})")
                    return current_url, [], 'other'

            # Track final URL in case of redirects
            final_url = response.url
            normalized_final_url = normalize_url(final_url)

            # Parse HTML content if this URL hasn't been visited
            if normalized_final_url not in visited:
                visited.add(normalized_final_url)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract all links
                links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(final_url, href)
                    normalized_url = normalize_url(full_url)

                    # Keep only links within the same domain
                    if urlparse(normalized_url).netloc == base_netloc:
                        links.append(normalized_url)
                return normalized_final_url, links, 'html'

            else:
                # print(f"Skipping already visited URL: {normalized_final_url}")
                return normalized_final_url, [], 'html'

        except requests.RequestException as e:
            retries += 1
            # print(f"Failed to retrieve {current_url} (Attempt {retries}): {e}")
            time.sleep(1)  # Wait before retrying
    # print(f"Failed to retrieve {current_url} after {max_retries} attempts.")
    failed_links.append(current_url)  # Add to the failed links list
    return current_url, [], 'error'

def get_all_website_links(url, max_threads=500):
    visited = set()
    to_visit = {normalize_url(url)}
    base_netloc = urlparse(url).netloc

    # Lists to store non-HTML links by type
    pdf_links = []
    zip_links = []
    other_non_html_links = []
    failed_links = []  # List to store failed URLs
    try:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            while to_visit:
                # print(f"Starting to crawl {len(to_visit)} links...")
                futures = {executor.submit(fetch_url, url, base_netloc, visited, failed_links): url for url in to_visit}
                to_visit.clear()

                for future in as_completed(futures):
                    current_url, found_links, content_type = future.result()

                    # print(f"Visited: {len(visited)} unique links; Currently Crawling: {current_url}")
                    # print(f"Found {len(found_links)} new links on {current_url}")

                    # Add unvisited HTML links to the `to_visit` set
                    for link in found_links:
                        if link not in visited and link not in to_visit:
                            to_visit.add(link)

                    # Add non-HTML links to their respective lists
                    if content_type == 'pdf':
                        pdf_links.append(current_url)
                    elif content_type == 'zip':
                        zip_links.append(current_url)
                    elif content_type == 'other':
                        other_non_html_links.append(current_url)

                # print(f"Completed batch. Total visited links: {len(visited)}\n")
        logger.info(f"PDF links found: {len(pdf_links)}, ZIP links found: {len(zip_links)}, Other non-HTML links found: {len(other_non_html_links)}  line 112 in crawling_links.py")
        logger.info(f"Failed links found: {len(failed_links)} line 113 in crawling_links.py")
        logger.info(f"Crawling complete. Total unique links found: {len(visited)} line 114 in crawling_links.py")

        return {
            "visited_links": list(visited),
            "pdf_links": pdf_links,
            "zip_links": zip_links,
            "other_non_html_links": other_non_html_links,
            "failed_links": list(set(failed_links)),
        }
    except Exception as e:
        logger_error.error(f"Get all Website Function Failed in crawling_links : {str(e)} line 124 in crawling_links.py")
        

def combined_links(visited_links, pdf_links, other_non_html_links):
    links = []
    extensions = set()
    try:
        for link in other_non_html_links:
            ext = link.split('.')[-1]
            if ext not in ['gif', 'zip', 'jpeg', 'jpg', 'png', 'svg', 'asc']:
                extensions.add(ext)
                links.append(link)
        visited_links.extend(pdf_links)
        links.extend(visited_links)
        logger.info(f"Total Links to scrape data : {links}")
        return links
    except Exception as e:
        logger_error.error(f"combined links Function Failed in crawling_links : {str(e)}  line 141 in crawling_links.py")