import unittest
from app import app

class TestAppFunctional(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_index_page(self):
        """Test the index page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SML', response.data)
        self.assertIn(b'Tasmota', response.data)
        self.assertIn(b'Dekoder', response.data)

    def test_decode_get_redirect(self):
        """Test that GET request to /decode redirects to index"""
        response = self.client.get('/decode')
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_decode_post_with_valid_data(self):
        """Test decoding with valid SML data"""
        test_data = """15:57:05.415 : 77 07 01 00 60 05 00 ff 01 01 01 01 65 00 1c 81 04 01 01 01 63 33 14 00 76 04 00 00 03 62 00 62 00 72 65 00 00 02 01 71
15:57:05.435 : 77 01 0b 0a 01 48 4c 59 02 00 01 1c 0f 01 01 f1 04
15:57:05.455 : 77 07 01 00 60 32 01 01 01 01 01 01 04 48 4c 59 01"""
        
        data = {'smldump': test_data}
        response = self.client.post('/decode', data=data)
        self.assertEqual(response.status_code, 200)
        # Should render the decode template
        self.assertIn(b'SML', response.data)

    def test_decode_post_with_invalid_data(self):
        """Test decoding with invalid SML data"""
        data = {'smldump': 'invalid sml data\nmore invalid data'}
        response = self.client.post('/decode', data=data)
        self.assertEqual(response.status_code, 200)
        # Should still render the decode template, but with parse errors
        self.assertIn(b'SML', response.data)

    def test_decode_post_with_empty_data(self):
        """Test decoding with empty data"""
        data = {'smldump': ''}
        response = self.client.post('/decode', data=data)
        self.assertEqual(response.status_code, 200)
        # Should render the decode template
        self.assertIn(b'SML', response.data)

    def test_decode_post_with_mixed_data(self):
        """Test decoding with mixed valid and invalid data"""
        test_data = """15:57:05.415 : 77 07 01 00 60 05 00 ff 01 01 01 01 65 00 1c 81 04 01 01 01 63 33 14 00 76 04 00 00 03 62 00 62 00 72 65 00 00 02 01 71
invalid line
77 07 01 00 60 32 01 01 01 01 01 01 04 48 4c 59 01
another invalid line"""
        
        data = {'smldump': test_data}
        response = self.client.post('/decode', data=data)
        self.assertEqual(response.status_code, 200)
        # Should render the decode template and handle errors gracefully
        self.assertIn(b'SML', response.data)

    def test_form_parameters(self):
        """Test that the form uses the correct parameter name"""
        # Test with wrong parameter name
        data = {'wrong_param': 'test data'}
        response = self.client.post('/decode', data=data)
        # Should handle missing parameter gracefully
        self.assertEqual(response.status_code, 500)  # or handle error appropriately

if __name__ == "__main__":
    unittest.main()
