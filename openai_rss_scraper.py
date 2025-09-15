#!/usr/bin/env python3
"""
OpenAI RSS Feed Scraper
Alternative approach using RSS feed if available
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import xml.etree.ElementTree as ET

def try_rss_feed():
    """Try to get OpenAI posts from RSS feed"""
    rss_urls = [
        "https://openai.com/blog/rss.xml",
        "https://openai.com/rss",
        "https://openai.com/feed",
        "https://openai.com/blog/feed"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    for rss_url in rss_urls:
        try:
            print(f"Trying RSS feed: {rss_url}")
            response = requests.get(rss_url, headers=headers, timeout=10)

            if response.status_code == 200:
                print(f"Success! Found RSS feed at {rss_url}")

                # Parse RSS XML
                root = ET.fromstring(response.content)

                articles = []

                # Handle different RSS formats
                items = root.findall('.//item') or root.findall('.//{http://purl.org/rss/1.0/}item')

                for item in items[:10]:  # Get first 10
                    title = item.find('title')
                    link = item.find('link')
                    description = item.find('description')
                    pub_date = item.find('pubDate')

                    article = {
                        'title': title.text if title is not None else 'No title',
                        'link': link.text if link is not None else '',
                        'description': description.text if description is not None else '',
                        'date': pub_date.text if pub_date is not None else '',
                        'scraped_at': datetime.now().isoformat()
                    }

                    articles.append(article)

                return articles

        except Exception as e:
            print(f"Failed to fetch {rss_url}: {e}")
            continue

    return []

def try_alternative_endpoints():
    """Try alternative OpenAI endpoints that might be less protected"""
    endpoints = [
        "https://openai.com/research",
        "https://openai.com/blog/tags/research",
        "https://openai.com/api/blog"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    for endpoint in endpoints:
        try:
            print(f"Trying endpoint: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)

            if response.status_code == 200:
                print(f"Success! Got response from {endpoint}")

                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for any links that might be blog posts
                links = soup.find_all('a', href=lambda x: x and '/blog/' in str(x))

                articles = []
                for link in links[:5]:
                    title = link.get_text().strip()
                    href = link.get('href')

                    if title and href and len(title) > 10:  # Filter out short/empty titles
                        if not href.startswith('http'):
                            href = f"https://openai.com{href}"

                        articles.append({
                            'title': title,
                            'link': href,
                            'source': endpoint,
                            'scraped_at': datetime.now().isoformat()
                        })

                if articles:
                    return articles

        except Exception as e:
            print(f"Failed to fetch {endpoint}: {e}")
            continue

    return []

def display_posts(posts, source="RSS Feed"):
    """Display posts in a readable format"""
    print(f"\n{'='*60}")
    print(f"OpenAI Posts from {source} - {len(posts)} found")
    print(f"{'='*60}")

    for i, post in enumerate(posts, 1):
        print(f"\n{i}. {post['title']}")
        print(f"   Link: {post['link']}")
        if post.get('date'):
            print(f"   Date: {post['date']}")
        if post.get('description'):
            desc = post['description'][:200] + "..." if len(post['description']) > 200 else post['description']
            print(f"   Description: {desc}")
        print("-" * 60)

def create_demo_data():
    """Create demo data showing what the scraper would return"""
    print("Creating demo data to show expected output format...")

    demo_posts = [
        {
            'title': 'GPT-4 Turbo with Vision',
            'link': 'https://openai.com/blog/gpt-4-turbo-with-vision',
            'description': 'We are rolling out GPT-4 Turbo with vision, our latest and most capable model.',
            'date': '2023-11-06',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'title': 'DALL·E 3 is now available in ChatGPT Plus and Enterprise',
            'link': 'https://openai.com/blog/dall-e-3-is-now-available-in-chatgpt-plus-and-enterprise',
            'description': 'ChatGPT can now generate images with DALL·E 3.',
            'date': '2023-10-19',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'title': 'OpenAI DevDay: Opening Keynote',
            'link': 'https://openai.com/blog/openai-devday',
            'description': 'New models and developer products announced at our first developer conference.',
            'date': '2023-11-06',
            'scraped_at': datetime.now().isoformat()
        }
    ]

    return demo_posts

def main():
    """Main function"""
    print("OpenAI Alternative Scraper")
    print("==========================")

    # Try RSS feed first
    posts = try_rss_feed()

    if not posts:
        print("\nRSS feed not found or accessible. Trying alternative endpoints...")
        posts = try_alternative_endpoints()

    if posts:
        display_posts(posts)

        # Save to JSON
        with open('openai_posts.json', 'w') as f:
            json.dump(posts, f, indent=2)
        print(f"\nSaved {len(posts)} posts to openai_posts.json")

    else:
        print("\nNo posts found from any source. Showing demo data instead:")
        demo_posts = create_demo_data()
        display_posts(demo_posts, "Demo Data")

        # Save demo data
        with open('openai_posts_demo.json', 'w') as f:
            json.dump(demo_posts, f, indent=2)
        print(f"\nSaved demo data to openai_posts_demo.json")

if __name__ == "__main__":
    main()