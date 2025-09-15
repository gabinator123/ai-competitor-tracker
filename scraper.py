#!/usr/bin/env python3
"""
AI Competitor Tracker - Web Scraper
Monitors AI companies and generates competitive intelligence reports
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time

class CompetitorTracker:
    def __init__(self, config_path='config.json'):
        """Initialize the tracker with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_website(self, company, url):
        """Scrape a single website for news and updates"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract basic information
            articles = []

            # Look for common article patterns
            article_selectors = [
                'article',
                '.blog-post',
                '.news-item',
                '.post',
                '[class*="article"]'
            ]

            for selector in article_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements[:5]:  # Limit to first 5
                        title = self.extract_title(element)
                        link = self.extract_link(element, url)
                        date = self.extract_date(element)

                        if title:
                            articles.append({
                                'title': title,
                                'link': link,
                                'date': date,
                                'company': company
                            })
                    break

            return articles

        except Exception as e:
            print(f"Error scraping {company} ({url}): {str(e)}")
            return []

    def extract_title(self, element):
        """Extract article title from element"""
        title_selectors = ['h1', 'h2', 'h3', '.title', '[class*="title"]']
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                return title_elem.get_text().strip()
        return None

    def extract_link(self, element, base_url):
        """Extract article link from element"""
        link_elem = element.select_one('a')
        if link_elem and link_elem.get('href'):
            href = link_elem['href']
            if href.startswith('http'):
                return href
            else:
                from urllib.parse import urljoin
                return urljoin(base_url, href)
        return None

    def extract_date(self, element):
        """Extract article date from element"""
        date_selectors = ['time', '.date', '[class*="date"]', '[datetime]']
        for selector in date_selectors:
            date_elem = element.select_one(selector)
            if date_elem:
                return date_elem.get_text().strip()
        return None

    def scrape_all_competitors(self):
        """Scrape all configured competitors"""
        all_articles = []

        for company, url in self.config['competitors'].items():
            print(f"Scraping {company}...")
            articles = self.scrape_website(company, url)
            all_articles.extend(articles)
            time.sleep(2)  # Be respectful with requests

        return all_articles

    def generate_report(self, articles):
        """Generate markdown report from scraped articles"""
        today = datetime.now().strftime('%Y-%m-%d')
        report_content = f"""# AI Competitor Intelligence Report - {today}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
Found {len(articles)} recent articles/updates across competitors.

"""

        # Group articles by company
        by_company = {}
        for article in articles:
            company = article['company']
            if company not in by_company:
                by_company[company] = []
            by_company[company].append(article)

        # Add company sections
        for company, company_articles in by_company.items():
            report_content += f"## {company}\n\n"

            for article in company_articles:
                title = article['title']
                link = article['link'] or 'No link available'
                date = article['date'] or 'Date not found'

                report_content += f"- **{title}**\n"
                report_content += f"  - Link: {link}\n"
                report_content += f"  - Date: {date}\n\n"

        return report_content

    def save_report(self, report_content):
        """Save report to reports directory"""
        os.makedirs('reports', exist_ok=True)
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"reports/competitor-report-{today}.md"

        with open(filename, 'w') as f:
            f.write(report_content)

        print(f"Report saved to {filename}")

    def run_daily_scan(self):
        """Run the complete daily scanning process"""
        print("Starting AI competitor tracking...")
        articles = self.scrape_all_competitors()
        report = self.generate_report(articles)
        self.save_report(report)
        print("Daily scan completed!")

def main():
    """Main entry point"""
    tracker = CompetitorTracker()
    tracker.run_daily_scan()

if __name__ == "__main__":
    main()