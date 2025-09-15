#!/usr/bin/env python3
"""
Simple OpenAI Blog Scraper
Gets the latest blog posts from OpenAI's website
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

def scrape_openai_blog():
    """Scrape OpenAI blog for latest posts"""
    url = "https://openai.com/blog"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    try:
        print(f"Fetching {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find blog post articles
        articles = []

        # Look for article elements or blog post containers
        post_selectors = [
            'article',
            '[data-testid*="post"]',
            '.blog-post',
            '.post-item',
            'a[href*="/blog/"]'
        ]

        blog_posts = []

        # Try different selectors to find blog posts
        for selector in post_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} elements with selector: {selector}")
                blog_posts = elements
                break

        # If no specific selectors work, look for links containing /blog/
        if not blog_posts:
            blog_posts = soup.find_all('a', href=lambda x: x and '/blog/' in x and x != '/blog')

        print(f"Processing {len(blog_posts)} blog posts...")

        for post in blog_posts[:10]:  # Get first 10 posts
            try:
                # Extract title
                title = None
                title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '[class*="title"]']

                for title_sel in title_selectors:
                    title_elem = post.find(title_sel)
                    if title_elem:
                        title = title_elem.get_text().strip()
                        break

                # If no title found in post, use the link text
                if not title and post.name == 'a':
                    title = post.get_text().strip()

                # Extract link
                link = None
                if post.name == 'a' and post.get('href'):
                    link = post['href']
                else:
                    link_elem = post.find('a')
                    if link_elem and link_elem.get('href'):
                        link = link_elem['href']

                # Make link absolute if it's relative
                if link and not link.startswith('http'):
                    link = f"https://openai.com{link}"

                # Extract date/time
                date = None
                date_selectors = ['time', '.date', '[class*="date"]', '[datetime]']
                for date_sel in date_selectors:
                    date_elem = post.find(date_sel)
                    if date_elem:
                        date = date_elem.get('datetime') or date_elem.get_text().strip()
                        break

                # Extract excerpt/description
                excerpt = None
                excerpt_selectors = ['.excerpt', '.description', 'p']
                for exc_sel in excerpt_selectors:
                    exc_elem = post.find(exc_sel)
                    if exc_elem:
                        excerpt = exc_elem.get_text().strip()[:200] + "..." if len(exc_elem.get_text().strip()) > 200 else exc_elem.get_text().strip()
                        break

                if title and link:
                    articles.append({
                        'title': title,
                        'link': link,
                        'date': date,
                        'excerpt': excerpt,
                        'scraped_at': datetime.now().isoformat()
                    })

            except Exception as e:
                print(f"Error processing post: {e}")
                continue

        return articles

    except Exception as e:
        print(f"Error scraping OpenAI blog: {e}")
        return []

def display_posts(posts):
    """Display posts in a readable format"""
    print(f"\n{'='*60}")
    print(f"OpenAI Blog Posts - {len(posts)} found")
    print(f"{'='*60}")

    for i, post in enumerate(posts, 1):
        print(f"\n{i}. {post['title']}")
        print(f"   Link: {post['link']}")
        if post['date']:
            print(f"   Date: {post['date']}")
        if post['excerpt']:
            print(f"   Excerpt: {post['excerpt']}")
        print("-" * 60)

def save_posts_json(posts, filename="openai_posts.json"):
    """Save posts to JSON file"""
    with open(filename, 'w') as f:
        json.dump(posts, f, indent=2)
    print(f"\nSaved {len(posts)} posts to {filename}")

def main():
    """Main function"""
    print("OpenAI Blog Scraper")
    print("==================")

    posts = scrape_openai_blog()

    if posts:
        display_posts(posts)
        save_posts_json(posts)
    else:
        print("No posts found or error occurred during scraping.")

if __name__ == "__main__":
    main()