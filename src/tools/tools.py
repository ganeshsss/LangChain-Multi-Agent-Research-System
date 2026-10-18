from langchain.tools import tool
import requests
from dotenv import load_dotenv
import os
from tavily import TavilyClient
from rich import print
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re



load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query :str) -> str:
    """
    Search the web for recent and reliable information on a topic.Returns a Titles,URLS,
    Sniippet and content of the top 5 search results.
    """

    results = tavily.search(query=query, max_results=5)

    out = []

    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content'][:300]}\n"
        )

    return "\n---\n".join(out)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
MAX_CHARS = 4000


@tool
def scrape_url(url: str) -> str:
    """
    Scrape a web page and return its main readable text.
    Use this to read the full content of a URL found via web search.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching {url}: {e}"

    if "text/html" not in resp.headers.get("Content-Type", ""):
        return f"Skipped {url}: not an HTML page."

    html = resp.text

    # 1. Best extractor first
    text = trafilatura.extract(html, include_comments=False, include_tables=True)

    # 2. Fallback: readability + BeautifulSoup
    if not text:
        try:
            summary_html = Document(html).summary()
            text = BeautifulSoup(summary_html, "lxml").get_text(separator="\n", strip=True)
        except Exception:
            text = None

    # 3. Last resort: plain BeautifulSoup cleanup
    if not text:
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)

    if not text:
        return f"No readable content found at {url}"

    text = re.sub(r"\n{3,}", "\n\n", text)  # collapse extra blank lines
    return text[:MAX_CHARS]