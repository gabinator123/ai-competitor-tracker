#!/usr/bin/env python3
"""
Google AI Blog Scraper
Gets the latest blog posts from Google's AI blog
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import xml.etree.ElementTree as ET

def scrape_google_ai_blog():
    """Scrape Google AI blog for latest posts"""

    # Try RSS feed first
    rss_urls = [
        "https://blog.google/technology/ai/rss/",
        "https://ai.googleblog.com/feeds/posts/default",
        "https://blog.google/rss/"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    # Try RSS feeds first
    for rss_url in rss_urls:
        try:
            print(f"Trying RSS feed: {rss_url}")
            response = requests.get(rss_url, headers=headers, timeout=10)

            if response.status_code == 200:
                print(f"Success! Found RSS feed at {rss_url}")
                result = parse_rss_feed(response.content, rss_url)
                if result and len([p for p in result if p['title'] != 'No title']) > 0:
                    return result
                else:
                    print(f"RSS feed found but parsing failed, trying next...")

        except Exception as e:
            print(f"Failed RSS feed {rss_url}: {e}")
            continue

    # If RSS fails, try direct scraping
    print("RSS feeds failed, trying direct scraping...")
    return scrape_google_ai_direct()

def parse_rss_feed(content, source_url):
    """Parse RSS feed content"""
    try:
        articles = []

        # Handle different XML namespaces
        try:
            root = ET.fromstring(content)
        except ET.ParseError as e:
            print(f"XML parsing error: {e}")
            return []

        # Look for items in different RSS formats
        items = (root.findall('.//item') or
                root.findall('.//{http://purl.org/rss/1.0/}item') or
                root.findall('.//{http://www.w3.org/2005/Atom}entry'))

        for item in items[:10]:  # Get first 10
            try:
                # Handle both RSS and Atom formats
                title_elem = (item.find('title') or
                            item.find('.//{http://www.w3.org/2005/Atom}title'))

                link_elem = (item.find('link') or
                           item.find('.//{http://www.w3.org/2005/Atom}link'))

                desc_elem = (item.find('description') or
                           item.find('.//{http://www.w3.org/2005/Atom}summary') or
                           item.find('.//{http://www.w3.org/2005/Atom}content'))

                date_elem = (item.find('pubDate') or
                           item.find('.//{http://www.w3.org/2005/Atom}published') or
                           item.find('.//{http://www.w3.org/2005/Atom}updated'))

                # Extract data
                title = title_elem.text if title_elem is not None else 'No title'

                # Handle link extraction
                link = ''
                if link_elem is not None:
                    if link_elem.text:
                        link = link_elem.text
                    elif link_elem.get('href'):  # Atom format
                        link = link_elem.get('href')

                description = desc_elem.text if desc_elem is not None else ''
                date = date_elem.text if date_elem is not None else ''

                # Clean up description (remove HTML tags if present)
                if description:
                    soup = BeautifulSoup(description, 'html.parser')
                    description = soup.get_text().strip()
                    if len(description) > 300:
                        description = description[:300] + "..."

                article = {
                    'title': title.strip(),
                    'link': link.strip(),
                    'description': description,
                    'date': date,
                    'source': 'Google AI RSS',
                    'scraped_at': datetime.now().isoformat()
                }

                articles.append(article)

            except Exception as e:
                print(f"Error parsing RSS item: {e}")
                continue

        return articles

    except Exception as e:
        print(f"Error parsing RSS feed: {e}")
        return []

def scrape_google_ai_direct():
    """Direct scraping of Google AI blog pages"""
    urls_to_try = [
        "https://blog.google/technology/ai/",
        "https://ai.googleblog.com/",
        "https://research.google/blog/"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    for url in urls_to_try:
        try:
            print(f"Trying direct scraping: {url}")
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                print(f"Success! Scraping {url}")

                soup = BeautifulSoup(response.content, 'html.parser')
                articles = []

                # Look for different article patterns - more specific selectors first
                article_selectors = [
                    'article h2 a',
                    'article h3 a',
                    '.blog-post a',
                    '.post-title a',
                    'h2 a[href*="/technology/ai/"]',
                    'h3 a[href*="/technology/ai/"]',
                    'a[href*="/technology/ai/"]:not([href*="twitter"]):not([href*="facebook"]):not([href*="linkedin"])',
                    'a[href*="googleblog.com"]:not([href*="twitter"]):not([href*="facebook"]):not([href*="linkedin"])'
                ]

                for selector in article_selectors:
                    elements = soup.select(selector)
                    if elements and len(elements) >= 1:  # Found a promising selector
                        print(f"Using selector: {selector} (found {len(elements)} elements)")

                        for element in elements[:10]:
                            try:
                                # Extract title
                                title = extract_title(element)

                                # Extract link
                                link = extract_link(element, url)

                                # Extract date
                                date = extract_date(element)

                                # Extract description/excerpt
                                description = extract_description(element)

                                if title and len(title) > 5:  # Filter out very short titles
                                    article = {
                                        'title': title,
                                        'link': link or url,
                                        'description': description,
                                        'date': date,
                                        'source': f'Google AI Direct ({url})',
                                        'scraped_at': datetime.now().isoformat()
                                    }
                                    articles.append(article)

                            except Exception as e:
                                print(f"Error processing element: {e}")
                                continue

                        if articles:
                            return articles
                        break

                # If no articles found with selectors, try finding any AI-related links
                if not articles:
                    print("No articles found with selectors, trying AI-related links...")
                    ai_links = soup.find_all('a', href=True)

                    for link_elem in ai_links[:20]:
                        href = link_elem.get('href', '')
                        text = link_elem.get_text().strip()

                        # Look for AI-related content
                        if (('ai' in href.lower() or 'artificial' in text.lower() or
                             'machine learning' in text.lower() or 'ml' in text.lower()) and
                            len(text) > 10 and len(text) < 200):

                            if not href.startswith('http'):
                                if href.startswith('/'):
                                    href = f"https://blog.google{href}"
                                else:
                                    href = f"{url.rstrip('/')}/{href}"

                            articles.append({
                                'title': text,
                                'link': href,
                                'description': '',
                                'date': '',
                                'source': f'Google AI Links ({url})',
                                'scraped_at': datetime.now().isoformat()
                            })

                    return articles[:10]  # Return first 10

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            continue

    return []

def extract_title(element):
    """Extract title from element"""
    title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '[class*="title"]', '[class*="headline"]']

    for selector in title_selectors:
        title_elem = element.select_one(selector)
        if title_elem:
            return title_elem.get_text().strip()

    # If no title found and element is a link, use link text
    if element.name == 'a':
        return element.get_text().strip()

    return None

def extract_link(element, base_url):
    """Extract link from element"""
    if element.name == 'a' and element.get('href'):
        href = element['href']
    else:
        link_elem = element.select_one('a')
        if link_elem and link_elem.get('href'):
            href = link_elem['href']
        else:
            return None

    # Make link absolute
    if href and not href.startswith('http'):
        if href.startswith('/'):
            if 'googleblog.com' in base_url:
                href = f"https://ai.googleblog.com{href}"
            else:
                href = f"https://blog.google{href}"
        else:
            href = f"{base_url.rstrip('/')}/{href}"

    return href

def extract_date(element):
    """Extract date from element"""
    date_selectors = ['time', '.date', '[class*="date"]', '[datetime]', '[class*="publish"]']

    for selector in date_selectors:
        date_elem = element.select_one(selector)
        if date_elem:
            return date_elem.get('datetime') or date_elem.get_text().strip()

    return None

def extract_description(element):
    """Extract description from element"""
    desc_selectors = ['.excerpt', '.description', '.summary', 'p']

    for selector in desc_selectors:
        desc_elem = element.select_one(selector)
        if desc_elem:
            desc = desc_elem.get_text().strip()
            if len(desc) > 20:  # Only return substantial descriptions
                return desc[:300] + "..." if len(desc) > 300 else desc

    return None

def display_posts(posts):
    """Display posts in readable format"""
    print(f"\n{'='*60}")
    print(f"Google AI Blog Posts - {len(posts)} found")
    print(f"{'='*60}")

    for i, post in enumerate(posts, 1):
        print(f"\n{i}. {post['title']}")
        print(f"   Link: {post['link']}")
        if post.get('date'):
            print(f"   Date: {post['date']}")
        if post.get('description'):
            print(f"   Description: {post['description']}")
        print(f"   Source: {post['source']}")
        print("-" * 60)

def save_posts_json(posts, filename="google_ai_posts.json"):
    """Save posts to JSON file"""
    with open(filename, 'w') as f:
        json.dump(posts, f, indent=2)
    print(f"\nSaved {len(posts)} posts to {filename}")

def main():
    """Main function"""
    print("Google AI Blog Scraper")
    print("=====================")

    posts = scrape_google_ai_blog()

    if posts:
        display_posts(posts)
        save_posts_json(posts)
    else:
        print("No posts found or error occurred during scraping.")

if __name__ == "__main__":
    main()