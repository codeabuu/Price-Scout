from typing import Optional  # For type hints
import bs4  # Import bs4 from Beautiful Soup
from asyncio import gather


async def get_stock(product_div: bs4.element.Tag) -> list[bs4.element.Tag]:
  """
  Asynchronously query and filter stock-related elements within a product div.

  Args:
      product_div: A reference to the product's HTML div element (BeautifulSoup Tag).

  Returns:
      A list of stock-related elements found within the product div.
  """

  # Query all elements with class '.a-size-base' within the product div
  elements = await product_div.query_selector_all('.a-size-base')

  # Filter elements containing the word 'stock' in their inner text
  filtered_elements = [element for element in elements if 'stock' in (await element.inner_text()).lower()]

  return filtered_elements

async def get_product(product_div: bs4.element.Tag) -> dict[str, Optional[str]]:
  """
  Asynchronously retrieve various attributes and texts related to a product.

  Args:
      product_div: A reference to the product's HTML div element (BeautifulSoup Tag).

  Returns:
      A dictionary containing extracted product information with keys 'img', 'name', 'price', 'url'.
      Values can be None if the element or parsing fails.
  """

  # Asynchronously query elements related to the product
  image_element_future = product_div.query_selector('img.s-image')
  name_element_future = product_div.query_selector('h2 a span')
  price_element_future = product_div.query_selector('span.a-offscreen')
  url_element_future = product_div.query_selector('a.a-link-normal.s-no-hover.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')

  # Await all element queries simultaneously
  image_element, name_element, price_element, url_element = await gather(
      image_element_future,
      name_element_future,
      price_element_future,
      url_element_future,
  )

  # Extract attributes and texts with error handling
  image_url = await image_element.get_attribute('src') if image_element else None
  product_name = await name_element.inner_text() if name_element else None
  product_price = None
  try:
      # Attempt to parse and clean up product price, converting to float
      product_price = float((await price_element.inner_text()).replace("$", "").replace(",", "").strip()) if price_element else None
  except ValueError:
      pass  # Silently ignore parsing errors

  product_url = "/".join((await url_element.get_attribute('href')).split("/")[:4]) if url_element else None

  # Return a dictionary containing extracted product information
  return {"img": image_url, "name": product_name, "price": product_price, "url": product_url}