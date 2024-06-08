import unittest
from flask_testing import TestCase
from Backend.app import app, db, ProductResult, TrackedProducts
from datetime import datetime

class MyTest(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite:///test_database.db"
    TESTING = True

    def create_app(self):
        app.config.from_object(self)
        return app

    def setUp(self):
        db.create_all()

        # Add sample data
        sample_product = ProductResult(
            name="Sample Product",
            url="http://example.com",
            img="http://example.com/img.jpg",
            price=19.99,
            search_text="sample search",
            source="example.com"
        )
        db.session.add(sample_product)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Test cases

    def test_add_tracked_product(self):
        response = self.client.post('/add-tracked-product', json={'name': 'New Product'})
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('id', data)
        self.assertEqual(data['message'], 'Tracked product added successfully')

    def test_get_tracked_products(self):
        response = self.client.get('/tracked-products')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(len(data) > 0)
        self.assertIn('name', data[0])

    def test_toggle_tracked_product(self):
        tracked_product = TrackedProducts(name="Toggle Product")
        db.session.add(tracked_product)
        db.session.commit()

        response = self.client.put(f'/tracked-product/{tracked_product.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['message'], 'Tracked product toggled successfully')

        updated_product = TrackedProducts.query.get(tracked_product.id)
        self.assertFalse(updated_product.tracked)

    def test_submit_results(self):
        results = [
            {'name': 'Test Product', 'url': 'http://example.com', 'img': 'http://example.com/img.jpg', 'price': 29.99}
        ]
        response = self.client.post('/results', json={'data': results, 'search_text': 'test search', 'source': 'test source'})
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['message'], 'Received data successfully')

        products = ProductResult.query.all()
        self.assertEqual(len(products), 2)  # One sample product plus one new product

    def test_get_product_results(self):
        response = self.client.get('/results?search_text=sample search')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(len(data) > 0)
        self.assertIn('name', data[0])
        self.assertIn('priceHistory', data[0])

    def test_unique_search_texts(self):
        response = self.client.get('/unique_search_texts')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(len(data) > 0)
        self.assertIn('sample search', data)

    def test_get_all_results(self):
        response = self.client.get('/all-results')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(len(data) > 0)
        self.assertIn('name', data[0])
        self.assertIn('url', data[0])

if __name__ == '__main__':
    unittest.main()
