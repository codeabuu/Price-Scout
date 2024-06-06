from asyncio import gather

async def get_stock(product_div):
    """
    Asynchronously query and filter stock-related elements within a product div.

    Args:
        product_div: A reference to the product's HTML div element.

    Returns:
        A list of stock-related elements found within the product div.
    """
    # Query all elements with class '.a-size-base' within the product div
    elements = await product_div.query_selector_all('.a-size-base')
    
    # Filter elements to select those containing the word 'stock' in their inner text
    filtered_elements = [element for element in elements if 'stock' in await element.inner_text()]
    
    return filtered_elements

async def get_product(product_div):
    """
    Asynchronously retrieve various attributes and texts related to a product.

    Args:
        product_div: A reference to the product's HTML div element.

    Returns:
        A dictionary containing extracted product information.
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

    # Retrieve attributes and texts from the elements
    image_url = await image_element.get_attribute('src') if image_element else None
    product_name = await name_element.inner_text() if name_element else None
    try:
        # Attempt to parse and clean up product price
        product_price = float((await price_element.inner_text()).replace("$", "").replace(",", "").strip()) if price_element else None
    except:
        # Handle cases where price parsing fails
        product_price = None
    product_url = "/".join((await url_element.get_attribute('href')).split("/")[:4]) if url_element else None

    # Return a dictionary containing extracted product information
    return {"img": image_url, "name": product_name, "price": product_price, "url": product_url}
