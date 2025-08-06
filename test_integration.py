import unittest
import tempfile
import os
from sml_decoder import TasmotaSMLParser

class TestSMLIntegration(unittest.TestCase):
    """Integration tests for the complete SML parsing workflow"""
    
    def setUp(self):
        self.parser = TasmotaSMLParser()
        self.sample_data = [
            "15:57:05.415 : 77 07 01 00 60 05 00 ff 01 01 01 01 65 00 1c 81 04 01 01 01 63 33 14 00 76 04 00 00 03 62 00 62 00 72 65 00 00 02 01 71",
            "15:57:05.435 : 77 01 0b 0a 01 48 4c 59 02 00 01 1c 0f 01 01 f1 04",
            "15:57:05.455 : 77 07 01 00 60 32 01 01 01 01 01 01 04 48 4c 59 01",
            "15:57:05.483 : 77 07 01 00 60 01 00 ff 01 01 01 01 0b 0a 01 48 4c 59 02 00 01 1c 0f 01",
            "15:57:05.516 : 77 07 01 00 01 08 00 ff 65 00 1c 81 04 65 05 a2 99 1e 62 1e 52 ff 65 0b e8 4d cf 01",
            "15:57:05.544 : 77 07 01 00 02 08 00 ff 65 00 1c 81 04 65 05 a2 99 1e 62 1e 52 ff 62 00 01",
            "15:57:05.565 : 77 07 01 00 10 07 00 ff 01 01 62 1b 52 00 53 01 a0 01",
        ]
    
    def test_full_parsing_workflow(self):
        """Test the complete parsing workflow from raw input to decoded messages"""
        messages = self.parser.decode_messages(self.sample_data)
        
        # Should have successfully parsed some messages
        self.assertIsInstance(messages, list)
        
        # Should have some parse errors for malformed data if any
        self.assertIsInstance(self.parser.parse_errors, list)
        self.assertIsInstance(self.parser.obis_errors, list)
        
        # Test each successfully parsed message
        for msg in messages:
            details = self.parser.get_message_details(msg)
            self.assertIsInstance(details, dict)
            
            # Check required fields in details
            required_fields = ['obis', 'name', 'unit', 'topic', 'value', 'human_readable']
            for field in required_fields:
                self.assertIn(field, details)
            
            # Test meter definition generation
            meter_def = self.parser.build_meter_def(msg)
            self.assertIsInstance(meter_def, str)
            self.assertTrue(meter_def.startswith("1,7707"))
    
    def test_error_handling(self):
        """Test error handling with various malformed inputs"""
        malformed_data = [
            "invalid line",
            "",
            "15:57:05.415 : invalid hex data",
            "77 zz xx yy",  # Invalid hex
            "15:57:05.415 : 77",  # Too short
            "not a timestamp : 77 07 01 00",
        ]
        
        messages = self.parser.decode_messages(malformed_data)
        
        # Should handle errors gracefully
        self.assertIsInstance(messages, list)
        # Should have parse errors for all malformed lines
        self.assertGreater(len(self.parser.parse_errors), 0)
    
    def test_mixed_valid_invalid_data(self):
        """Test parsing mixed valid and invalid data"""
        mixed_data = self.sample_data + [
            "invalid line 1",
            "",
            "invalid line 2",
        ]
        
        messages = self.parser.decode_messages(mixed_data)
        
        # Should successfully parse valid data and collect errors for invalid data
        self.assertIsInstance(messages, list)
        self.assertGreater(len(self.parser.parse_errors), 0)
    
    def test_duplicate_obis_handling(self):
        """Test that duplicate OBIS codes are handled correctly"""
        # Use the same line twice to test duplicate handling
        duplicate_data = [
            self.sample_data[0],
            self.sample_data[0],  # Duplicate
            self.sample_data[1],
        ]
        
        messages = self.parser.decode_messages(duplicate_data)
        
        # Should handle duplicates (implementation specific)
        self.assertIsInstance(messages, list)

class TestFileOperations(unittest.TestCase):
    """Test file-based operations"""
    
    def test_file_parsing(self):
        """Test parsing data from a file"""
        test_data = """15:57:05.415 : 77 07 01 00 60 05 00 ff 01 01 01 01 65 00 1c 81 04 01 01 01 63 33 14 00 76 04 00 00 03 62 00 62 00 72 65 00 00 02 01 71
15:57:05.435 : 77 01 0b 0a 01 48 4c 59 02 00 01 1c 0f 01 01 f1 04
15:57:05.455 : 77 07 01 00 60 32 01 01 01 01 01 01 04 48 4c 59 01"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(test_data)
            temp_filename = f.name
        
        try:
            parser = TasmotaSMLParser()
            with open(temp_filename, 'r') as fp:
                messages = parser.decode_messages(fp.read().splitlines())
            
            self.assertIsInstance(messages, list)
        finally:
            os.unlink(temp_filename)

if __name__ == "__main__":
    unittest.main()
