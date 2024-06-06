import unittest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now, you can import modules from your backend directory
from Backend.scraper.amazon import get_stock, get_product


class TestProductFunctions(unittest.IsolatedAsyncioTestCase):
    async def test_get_stock(self):
        # Mock the product_div and its inner_text method
        product_div = MagicMock()
        product_div.query_selector_all.return_value = [
            AsyncMock(inner_text=AsyncMock(return_value='In stock')),
            AsyncMock(inner_text=AsyncMock(return_value='Out of stock'))
        ]

        # Call the function
        result = await get_stock(product_div)

        # Assert that only the 'In stock' element is returned
        self.assertEqual(len(result), 1)
        self.assertIn('In stock', await result[0].inner_text())

    async def test_get_product(self):
        # Mock the product_div and its query_selector and get_attribute methods
        product_div = MagicMock()
        product_div.query_selector.return_value = AsyncMock(
            return_value=MagicMock(get_attribute=AsyncMock(return_value='mock_url'))
        )
        product_div.query_selector_all.return_value = [
            AsyncMock(inner_text=AsyncMock(return_value='Product Name')),
            AsyncMock(inner_text=AsyncMock(return_value='$10.99')),
        ]

        # Call the function
        result = await get_product(product_div)

        # Assert the extracted product information
        self.assertEqual(result['name'], 'Product Name')
        self.assertEqual(result['price'], 10.99)
        self.assertEqual(result['url'], 'mock_url')


if __name__ == '__main__':
    unittest.main()
