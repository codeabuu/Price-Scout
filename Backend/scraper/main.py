import asyncio
from playwright.async_api import async_playwright
import json
import os
from amazon import get_product as get_amazon_product
from requests import post

# Base URL for Amazon searches
AMAZON = "https://amazon.ca"

# Dictionary mapping URLs to their specific selectors for searching and product extraction
URLS = {
    AMAZON: {
        "search_field_query": 'input[name="field-keywords"]',
        "search_button_query": 'input[value="Go"]',
        "product_selector": "div.s-card-container"
    }
}

available_urls = URLS.keys()


def load_auth():
    """Loads authentication credentials from a JSON file."""
    try:
        FILE = os.path.join("scraper", "auth.json")
        with open(FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("JSON file not found: auth.json")

# place your bright data credentials in auth.json file with keys: "username", "password" and "host"
cred = load_auth()
auth = f'{cred["username"]}:{cred["password"]}'
browser_url = f'wss://{auth}@{cred["host"]}'


async def search(metadata, page, search_text):
    """Searches the provided website using the given search text and selectors from metadata."""

    print(f"Searching for {search_text} on {page.url}")
    search_field_query = metadata.get("search_field_query")
    search_button_query = metadata.get("search_button_query")

    if search_field_query and search_button_query:
        print("Filling input field")
        try:
            search_box = await page.wait_for_selector(search_field_query)
            await search_box.type(search_text)
        except Exception as e:
            print(f"Error filling the search field: {e}")
            return None
        print("Pressing search button")
        try:
            button = await page.wait_for_selector(search_button_query)
            await button.click()
        except Exception as e:
            print(f"Error clicking search button: {e}")
            return None
    else:
        raise Exception("Could not search.")

    await page.wait_for_load_state()
    return page


async def get_products(page, search_text, selector, get_product):
    """Retrieves product information from the provided page using the selector and extracts details with the get_product_func."""

    print("Retreiving products.")
    if not page:
        print("Search page not found. Skipping product extraction.")
        return []
    product_divs = await page.query_selector_all(selector)
    valid_products = []
    words = search_text.split(" ")

    async with asyncio.TaskGroup() as tg:
        for div in product_divs:
            async def task(p_div):
                """Asynchronous task for processing each product individually."""
                try:
                    product = await get_product(p_div)

                    if not product["price"] or not product["url"]:
                        return

                    for word in words:
                        if not product["name"] or word.lower() not in product["name"].lower():
                            break
                    else:
                        valid_products.append(product)
                except Exception as e:
                    print(f"Error processing product: {e}")
            tg.create_task(task(div))

    return valid_products


def save_results(results):
    """Saves scraped results to a JSON file (assumed to be 'Scraper/results.json')."""

    data = {"results": results}
    FILE = os.path.join("Scraper", "results.json")
    with open(FILE, "w") as f:
        json.dump(data, f)


def post_results(results, endpoint, search_text, source):
    """Saves scraped results to a JSON file (assumed to be 'Scraper/results.json')."""

    headers = {
        "Content-Type": "application/json"
    }
    data = {"data": results, "search_text": search_text, "source": source}

    print("Sending request to", endpoint)
    response = post("http://localhost:5000" + endpoint,
                    headers=headers, json=data)
    print("Status code:", response.status_code)


async def main(url, search_text, response_route):
    """
    The main function that orchestrates the scraping process.

    Args:
        url (str): The URL of the website to scrape.
        search_text (str): The search text to use for finding products.
        response_route (str): The endpoint on the backend server to send scraped results.
    """

    metadata = URLS.get(url)
    if not metadata:
        print("Invalid URL.")
        return

    async with async_playwright() as pw:
        print('Connecting to browser.')
        try:
            browser = await pw.chromium.connect_over_cdp(browser_url)
            page = await browser.new_page()
            print("Connected.")
            await page.goto(url, timeout=120000)
            print("Loaded initial page.")
            search_page = await search(metadata, page, search_text)
        except Exception as e:
            print(f"Error during browser connection or navigation: {e}")
            return
        
        def func(x): return None

        # Assign product extraction function based on the URL
        if url == AMAZON:
            func = get_amazon_product
        else:
            raise Exception('Invalid URL')

        results = await get_products(search_page, search_text, metadata["product_selector"], func)
        print("Saving results.")
        post_results(results, response_route, search_text, url)

        await browser.close()
        print("Scrape completed.")

if __name__ == "__main__":
    # test script
    asyncio.run(main(AMAZON, "ryzen 9 3950x"))