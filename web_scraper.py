import aiohttp
import asyncio
from aiohttp import ClientTimeout
from bs4 import BeautifulSoup
import aiosqlite
from typing import List, Tuple, Optional


BASE_URL = 'https://economictimes.indiatimes.com'
TIMEOUT_SECONDS = 10000  # Increased timeout to 10000 seconds
MAX_RETRIES = 3       # Max number of retries for each request


# Asynchronous function to send request and get the soup object of the webpage
async def fetch_page_content(session: aiohttp.ClientSession, url: str, retries: int = MAX_RETRIES) -> Optional[BeautifulSoup]:
    """Fetches the content of the given URL asynchronously and returns a BeautifulSoup object.
    
    Implements a retry mechanism to handle timeouts.

    Args:
        session (aiohttp.ClientSession): The session object to use for making HTTP requests.
        url (str): The URL to fetch the content from.
        retries (int): The number of retry attempts in case of failure.

    Returns:
        Optional[BeautifulSoup]: Parsed HTML of the page or None in case of failure.
    """
    for attempt in range(retries):
        try:
            async with session.get(url, timeout=ClientTimeout(total=TIMEOUT_SECONDS)) as response:
                response.raise_for_status()  # Check if request was successful
                content = await response.text()
                return BeautifulSoup(content, 'html.parser')
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt + 1 == retries:
                print(f"Failed to retrieve the webpage {url} after {retries} attempts.")
                return None
            await asyncio.sleep(2)  # Add a small delay before retrying


# Function to extract article links from the page
def extract_articles(soup: BeautifulSoup) -> List[Tuple[str, str, str]]:
    """Extracts articles' title, synopsis, and link from the soup object.

    Args:
        soup (BeautifulSoup): The parsed HTML of the main page.

    Returns:
        List[Tuple[str, str, str]]: A list of tuples containing (title, synopsis, link).
    """
    articles = soup.find_all('div', class_='eachStory')
    article_list = []

    for article in articles:
        try:
            title = article.find('h3').text.strip() if article.find('h3') else 'No Title'
            synopsis = article.find('p').text.strip() if article.find('p') else 'No Synopsis'
            link = article.find('a')['href'] if article.find('a') else None

            if link:
                full_link = link if link.startswith('http') else BASE_URL + link
                article_list.append((title, synopsis, full_link))
        except Exception as e:
            print(f"Error processing article element: {e}")
    
    return article_list


# Asynchronous function to fetch content from individual article pages
async def get_article_content(session: aiohttp.ClientSession, link: str) -> str:
    """Fetches the full article content asynchronously from the given article link.

    Args:
        session (aiohttp.ClientSession): The session object to use for making HTTP requests.
        link (str): The full link to the article.

    Returns:
        str: The extracted article content or an error message.
    """
    soup = await fetch_page_content(session, link)
    if soup:
        try:
            article_content = soup.find('div', {'class': 'artText'}).get_text(separator=' ').strip()
            return article_content
        except AttributeError:
            return "Content not available"
    return "Failed to fetch content"


# Asynchronous function to fetch and append more articles using 'Load More' functionality
async def load_all_articles(session: aiohttp.ClientSession, base_url: str) -> List[Tuple[str, str, str]]:
    """Loads all the articles asynchronously using the 'Load More' functionality.

    Args:
        session (aiohttp.ClientSession): The session object to use for making HTTP requests.
        base_url (str): The base URL to scrape articles from.

    Returns:
        List[Tuple[str, str, str]]: A list of tuples containing (title, synopsis, link).
    """
    page_num = 1
    all_articles = []

    while True:
        load_more_url = f"{base_url}/lazyloadlistnew.cms?msid=13357919&curpg={page_num}&img=0"
        soup = await fetch_page_content(session, load_more_url)
        
        if not soup:
            break

        new_articles = extract_articles(soup)
        if not new_articles:
            break

        all_articles.extend(new_articles)
        page_num += 1  # Increment the page to fetch the next batch of articles

    return all_articles


# Asynchronous function to scrape and store data
async def scrape_and_store_articles(session: aiohttp.ClientSession, url: str) -> None:
    """Scrapes articles from the given URL asynchronously and stores them in an SQLite database.

    Args:
        session (aiohttp.ClientSession): The session object to use for making HTTP requests.
        url (str): The URL to scrape articles from.
    """    
    # Fetch the main page and initial articles
    soup = await fetch_page_content(session, url)
    if not soup:
        print("Failed to fetch main page. Exiting.")
        return

    # Extract initial articles' basic information
    articles = extract_articles(soup)

    # Load more articles using 'Load More' functionality
    more_articles = await load_all_articles(session, BASE_URL)
    articles.extend(more_articles)

    scraped_data = []

    # Fetch content for each article concurrently
    tasks = [get_article_content(session, link) for _, _, link in articles]
    article_contents = await asyncio.gather(*tasks)

    for i, (title, synopsis, link) in enumerate(articles):
        content = article_contents[i].replace("(You can now subscribe to our  Economic Times WhatsApp channel )", "").strip()
        content = content.replace("  ", " ").strip()
        content = "’s".join("’s".join(".".join(",".join(")".join("(".join(" ".join(content.split("  ")).split('( ')).split(' )')).split(" ,")).split(" .")).split(" ’s")).split("\'s"))
        if content == "Content not available":
            content = synopsis
        scraped_data.append((title, synopsis, link, content))

    # Store scraped data into SQLite
    await store_data_in_db(scraped_data)


# Asynchronous function to store data in SQLite
async def store_data_in_db(data: List[Tuple[str, str, str, str]]) -> None:
    """Stores the scraped data into an SQLite database asynchronously.

    Args:
        data (List[Tuple[str, str, str, str]]): A list of tuples containing (title, synopsis, link, content).
    """
    async with aiosqlite.connect('manufacturing_articles.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                synopsis TEXT,
                link TEXT,
                content TEXT
            )
        ''')

        await db.executemany('''
            INSERT INTO articles (title, synopsis, link, content)
            VALUES (?, ?, ?, ?)
        ''', data)

        await db.commit()
        print("Data successfully stored in the database.")


# Main function to execute the scraper asynchronously
async def main():
    url = 'https://economictimes.indiatimes.com/industry/indl-goods/svs/engineering'
    
    timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)  # Increase timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        await scrape_and_store_articles(session, url)


if __name__ == "__main__":
    asyncio.run(main())
