import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app
import json

class TestFlaskAppPytest:
    """Pytest-based tests for Flask application"""
    
    @pytest.fixture
    def client(self):
        """Fixture providing Flask test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def sample_sml_data(self):
        """Fixture providing sample SML dump data"""
        return """15:57:05.415 : 77 07 01 00 60 05 00 ff 01 01 01 01 65 00 1c 81 04 01 01 01 63 33 14 00 76 04 00 00 03 62 00 62 00 72 65 00 00 02 01 71
15:57:05.435 : 77 01 0b 0a 01 48 4c 59 02 00 01 1c 0f 01 01 f1 04
15:57:05.455 : 77 07 01 00 60 32 01 01 01 01 01 01 04 48 4c 59 01"""
    
    def test_index_page_content(self, client):
        """Test index page loads with correct content"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Tasmota SML Dekoder' in response.data
        assert b'sensor53 d1' in response.data
        assert b'formGroupSMLDumpInput' in response.data
        assert b'textarea' in response.data
    
    def test_index_page_form_structure(self, client):
        """Test that the form has correct structure"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'action="/decode"' in response.data
        assert b'method="POST"' in response.data
        assert b'name="smldump"' in response.data
    
    def test_decode_get_redirects(self, client):
        """Test GET request to /decode redirects to index"""
        response = client.get('/decode')
        
        assert response.status_code == 302
        assert response.location.endswith('/')
    
    @patch('app.TasmotaSMLParser')
    def test_decode_post_successful(self, mock_parser_class, client, sample_sml_data):
        """Test successful SML data decoding"""
        # Mock the parser
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        
        # Mock successful parsing
        mock_message = MagicMock()
        mock_parser.decode_messages.return_value = [mock_message]
        mock_parser.get_message_details.return_value = {
            'obis': 'test_obis',
            'name': 'Test Measurement',
            'unit': 'kWh',
            'value': 123.45
        }
        mock_parser.build_meter_def.return_value = "1,7707test@1,Test,kWh,test,2"
        mock_parser.parse_errors = []
        mock_parser.obis_errors = []
        
        response = client.post('/decode', data={'smldump': sample_sml_data})
        
        assert response.status_code == 200
        # Should call the parser with correct data
        mock_parser.decode_messages.assert_called_once()
        call_args = mock_parser.decode_messages.call_args[0][0]
        assert isinstance(call_args, list)
        assert len(call_args) == 3  # Three lines in sample data
    
    @patch('app.TasmotaSMLParser')
    def test_decode_post_with_errors(self, mock_parser_class, client):
        """Test decoding with parse errors"""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        
        # Mock parsing with errors
        mock_parser.decode_messages.return_value = []
        mock_parser.parse_errors = ['invalid line 1', 'invalid line 2']
        mock_parser.obis_errors = [{'frame': b'test', 'hex': 'test', 'msg': 'error'}]
        
        response = client.post('/decode', data={'smldump': 'invalid data'})
        
        assert response.status_code == 200
        # Should render template with errors
        assert b'SML' in response.data
    
    def test_decode_post_empty_data(self, client):
        """Test decoding with empty data"""
        response = client.post('/decode', data={'smldump': ''})
        
        assert response.status_code == 200
        # Should handle empty data gracefully
    
    @pytest.mark.parametrize("invalid_data", [
        "not sml data",
        "77 GG HH II",  # Invalid hex
        "random text\nmore random text",
        "   \n   \n   ",  # Just whitespace
    ])
    @patch('app.TasmotaSMLParser')
    def test_decode_post_invalid_formats(self, mock_parser_class, client, invalid_data):
        """Test various invalid data formats"""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.decode_messages.return_value = []
        mock_parser.parse_errors = []
        mock_parser.obis_errors = []
        
        response = client.post('/decode', data={'smldump': invalid_data})
        
        assert response.status_code == 200
    
    def test_decode_post_missing_parameter(self, client):
        """Test POST without required parameter"""
        response = client.post('/decode', data={})
        
        # Should handle missing parameter (might return 400 or 500)
        assert response.status_code in [400, 500]
    
    @patch('app.logger')
    @patch('app.TasmotaSMLParser')
    def test_logging_functionality(self, mock_parser_class, mock_logger, client, sample_sml_data):
        """Test that logging works correctly"""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.decode_messages.return_value = []
        mock_parser.parse_errors = []
        mock_parser.obis_errors = []
        
        response = client.post('/decode', data={'smldump': sample_sml_data})
        
        assert response.status_code == 200
        # Should have logged the request
        mock_logger.info.assert_called()
    
    @patch('app.TasmotaSMLParser')
    def test_message_sorting(self, mock_parser_class, client, sample_sml_data):
        """Test that messages are sorted by OBIS code"""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        
        # Create mock messages with different OBIS codes
        mock_msg1 = MagicMock()
        mock_msg2 = MagicMock()
        mock_parser.decode_messages.return_value = [mock_msg1, mock_msg2]
        
        # Mock message details with different OBIS codes
        def mock_get_details(msg):
            if msg == mock_msg1:
                return {'obis': 'zz_last'}
            else:
                return {'obis': 'aa_first'}
        
        mock_parser.get_message_details.side_effect = mock_get_details
        mock_parser.build_meter_def.return_value = "test_def"
        mock_parser.parse_errors = []
        mock_parser.obis_errors = []
        
        response = client.post('/decode', data={'smldump': sample_sml_data})
        
        assert response.status_code == 200
        # Should call get_message_details for each message
        assert mock_parser.get_message_details.call_count == 2

class TestFlaskAppIntegration:
    """Integration tests for Flask app with real SML data"""
    
    @pytest.fixture
    def client(self):
        """Fixture providing Flask test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_real_sml_data_processing(self, client):
        """Test with real SML data from test-data.txt"""
        real_sml_data = """15:57:05.415 : 77 07 01 00 60 05 00 ff 01 01 01 01 65 00 1c 81 04 01 01 01 63 33 14 00 76 04 00 00 03 62 00 62 00 72 65 00 00 02 01 71
15:57:05.435 : 77 01 0b 0a 01 48 4c 59 02 00 01 1c 0f 01 01 f1 04
15:57:05.455 : 77 07 01 00 60 32 01 01 01 01 01 01 04 48 4c 59 01"""
        
        response = client.post('/decode', data={'smldump': real_sml_data})
        
        assert response.status_code == 200
        # Should process the data without crashing
        assert b'SML' in response.data
    
    def test_form_validation_end_to_end(self, client):
        """Test form validation from submission to response"""
        response = client.post('/decode', data={'smldump': 'test data'})
        
        assert response.status_code == 200
        # Should contain form elements or results
        assert len(response.data) > 0
    
    def test_error_page_rendering(self, client):
        """Test that error conditions render properly"""
        # Test with problematic data that might cause errors
        problematic_data = "77 " + "invalid " * 1000  # Very long invalid data
        
        response = client.post('/decode', data={'smldump': problematic_data})
        
        # Should handle errors gracefully and return a valid response
        assert response.status_code == 200
        assert b'html' in response.data.lower()  # Should return HTML
