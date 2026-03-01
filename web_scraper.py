"""Simple web scraper and insight generator.

Usage:
    python web_scraper.py https://example.com --max-pages 5 --output insights.json
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, deque
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from typing import Dict, List, Set
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "to", "of", "in", "on", "for", "with",
    "is", "are", "was", "were", "be", "by", "this", "that", "it", "as", "at", "from",
    "your", "you", "our", "we", "they", "their", "he", "she", "his", "her", "not", "can",
    "will", "about", "into", "more", "than", "up", "out", "who", "what", "when", "where",
}


class SimpleHTMLExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = "Untitled"
        self.links: List[str] = []
        self.headings: List[str] = []
        self.paragraph_count = 0
        self.image_count = 0
        self.link_count = 0
        self.visible_text_parts: List[str] = []

        self._capture_title = False
        self._capture_heading = False
        self._current_heading = ""
        self._ignore_content = False

    def handle_starttag(self, tag: str, attrs: List[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag in {"script", "style", "noscript"}:
            self._ignore_content = True
            return

        if tag == "title":
            self._capture_title = True
        elif tag in {"h1", "h2", "h3"}:
            self._capture_heading = True
            self._current_heading = ""
        elif tag == "p":
            self.paragraph_count += 1
        elif tag == "img":
            self.image_count += 1
        elif tag == "a":
            self.link_count += 1
            href = attrs_dict.get("href")
            if href:
                self.links.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"}:
            self._ignore_content = False
            return

        if tag == "title":
            self._capture_title = False
        elif tag in {"h1", "h2", "h3"}:
            self._capture_heading = False
            if self._current_heading.strip() and len(self.headings) < 15:
                self.headings.append(self._current_heading.strip())

    def handle_data(self, data: str) -> None:
        if self._ignore_content:
            return

        stripped = data.strip()
        if not stripped:
            return

        self.visible_text_parts.append(stripped)

        if self._capture_title:
            self.title = stripped
        if self._capture_heading:
            self._current_heading += f" {stripped}"


@dataclass
class PageData:
    url: str
    title: str
    headings: List[str]
    paragraph_count: int
    image_count: int
    link_count: int
    word_count: int
    top_words: List[List[str | int]]


class WebScraper:
    def __init__(self, base_url: str, max_pages: int = 5, timeout: int = 15) -> None:
        self.base_url = base_url
        self.max_pages = max_pages
        self.timeout = timeout

    def _is_internal_link(self, link: str) -> bool:
        parsed_base = urlparse(self.base_url)
        parsed_link = urlparse(link)
        return parsed_base.netloc == parsed_link.netloc

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"[a-zA-Z]{3,}", text.lower())
        return [token for token in tokens if token not in STOPWORDS]

    def _fetch_html(self, url: str) -> str:
        request = Request(url, headers={"User-Agent": "BlogverseInsightScraper/1.0"})
        with urlopen(request, timeout=self.timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")

    def _parse_page(self, url: str) -> tuple[PageData, List[str]]:
        html = self._fetch_html(url)
        parser = SimpleHTMLExtractor()
        parser.feed(html)

        cleaned_text = " ".join(parser.visible_text_parts)
        tokens = self._tokenize(cleaned_text)
        word_freq = Counter(tokens)

        internal_links: List[str] = []
        for link in parser.links:
            joined = urljoin(url, link)
            normalized = joined.split("#")[0]
            if normalized.startswith("http") and self._is_internal_link(normalized):
                internal_links.append(normalized)

        page_data = PageData(
            url=url,
            title=parser.title,
            headings=parser.headings,
            paragraph_count=parser.paragraph_count,
            image_count=parser.image_count,
            link_count=parser.link_count,
            word_count=len(tokens),
            top_words=[[word, count] for word, count in word_freq.most_common(10)],
        )
        return page_data, internal_links

    def scrape(self) -> Dict:
        queue = deque([self.base_url])
        visited: Set[str] = set()
        pages: List[PageData] = []
        crawl_errors: List[Dict[str, str]] = []

        while queue and len(visited) < self.max_pages:
            current_url = queue.popleft()
            if current_url in visited:
                continue
            visited.add(current_url)

            try:
                page_data, links = self._parse_page(current_url)
                pages.append(page_data)
                for link in links:
                    if link not in visited and len(queue) + len(visited) < self.max_pages * 4:
                        queue.append(link)
            except (HTTPError, URLError, TimeoutError, ValueError) as exc:
                crawl_errors.append({"url": current_url, "error": str(exc)})

        return self._generate_report(pages, crawl_errors)

    def _generate_report(self, pages: List[PageData], crawl_errors: List[Dict[str, str]]) -> Dict:
        if not pages:
            return {
                "summary": {
                    "pages_scraped": 0,
                    "avg_word_count": 0,
                    "avg_links_per_page": 0,
                    "avg_images_per_page": 0,
                },
                "insights": [],
                "pages": [],
                "errors": crawl_errors,
            }

        total_words = sum(page.word_count for page in pages)
        total_links = sum(page.link_count for page in pages)
        total_images = sum(page.image_count for page in pages)

        global_words: Counter[str] = Counter()
        for page in pages:
            global_words.update({word: count for word, count in page.top_words})

        longest_page = max(pages, key=lambda p: p.word_count)
        shortest_page = min(pages, key=lambda p: p.word_count)

        insights = [
            f"Most content-heavy page: '{longest_page.title}' ({longest_page.word_count} meaningful words).",
            f"Least content-heavy page: '{shortest_page.title}' ({shortest_page.word_count} meaningful words).",
            f"Top recurring keywords across crawled pages: {', '.join([w for w, _ in global_words.most_common(8)])}.",
            f"Estimated reading time for average page: {max(1, round((total_words / len(pages)) / 200))} minute(s).",
        ]

        return {
            "summary": {
                "pages_scraped": len(pages),
                "avg_word_count": round(total_words / len(pages), 2),
                "avg_links_per_page": round(total_links / len(pages), 2),
                "avg_images_per_page": round(total_images / len(pages), 2),
                "top_global_words": [[word, count] for word, count in global_words.most_common(20)],
            },
            "insights": insights,
            "pages": [asdict(page) for page in pages],
            "errors": crawl_errors,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape a website and produce actionable insights.")
    parser.add_argument("url", help="Starting URL to crawl.")
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum number of pages to scrape.")
    parser.add_argument("--output", default="scrape_insights.json", help="Path to write JSON report.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scraper = WebScraper(args.url, max_pages=max(1, args.max_pages))
    report = scraper.scrape()

    with open(args.output, "w", encoding="utf-8") as outfile:
        json.dump(report, outfile, indent=2, ensure_ascii=False)

    print(f"Scraping completed. Pages scraped: {report['summary']['pages_scraped']}")
    print(f"Report saved to: {args.output}")
    if report["insights"]:
        print("\nInsights:")
        for idx, insight in enumerate(report["insights"], start=1):
            print(f"{idx}. {insight}")


if __name__ == "__main__":
    main()
