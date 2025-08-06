import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sml_decoder import TasmotaSMLParser

class TestSMLDecoder(unittest.TestCase):
    def setUp(self):
        self.parser = TasmotaSMLParser()
    
    def test_parse_input_with_timestamp(self):
        """Test parsing input with timestamp format"""
        input_line = "15:57:05.415 : 77 07 01 00 60 05 00 ff 01 01 01 01 65 00 1c 81 04 01 01 01 63 33 14 00 76 04 00 00 03 62 00 62 00 72 65 00 00 02 01 71"
        result = self.parser.parse_input(input_line)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, bytes)
    
    def test_parse_input_hex_only(self):
        """Test parsing input with hex only format"""
        input_line = "77 07 01 00 60 05 00 ff 01 01 01 01 65 00 1c 81 04 01 01 01 63 33 14 00 76 04 00 00 03 62 00 62 00 72 65 00 00 02 01 71"
        result = self.parser.parse_input(input_line)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, bytes)
    
    def test_parse_input_invalid(self):
        """Test parsing invalid input"""
        input_line = "invalid input"
        result = self.parser.parse_input(input_line)
        self.assertIsNone(result)
        self.assertIn(input_line, self.parser.parse_errors)
    
    def test_parse_input_empty(self):
        """Test parsing empty input"""
        input_line = ""
        result = self.parser.parse_input(input_line)
        self.assertIsNone(result)
        self.assertIn(input_line, self.parser.parse_errors)
    
    def test_decode_frame_valid(self):
        """Test decoding a valid SML frame"""
        # Valid SML frame from test data
        hex_data = "770701006005000ff010101016500001c8104010101016333140076040000036200620072650000020171"
        frame = bytes.fromhex(hex_data)
        result = self.parser.decode_frame(frame)
        # Result can be None, False, or a list of messages depending on frame content
        self.assertIsNotNone(result)
    
    def test_decode_messages_with_test_data(self):
        """Test decoding multiple messages with real test data"""
        test_lines = [
            "15:57:05.415 : 77 07 01 00 60 05 00 ff 01 01 01 01 65 00 1c 81 04 01 01 01 63 33 14 00 76 04 00 00 03 62 00 62 00 72 65 00 00 02 01 71",
            "15:57:05.435 : 77 01 0b 0a 01 48 4c 59 02 00 01 1c 0f 01 01 f1 04",
            "15:57:05.455 : 77 07 01 00 60 32 01 01 01 01 01 01 04 48 4c 59 01",
            "invalid line",  # This should be handled gracefully
            ""  # Empty line should be handled gracefully
        ]
        messages = self.parser.decode_messages(test_lines)
        self.assertIsInstance(messages, list)
        # Should have some parse errors due to invalid/empty lines
        self.assertGreater(len(self.parser.parse_errors), 0)
    
    def test_get_message_details(self):
        """Test getting message details for a valid message"""
        # This test requires a valid SML message object
        # We'll test with a mock message if needed
        pass  # Will be implemented when we have valid message objects
    
    def test_build_meter_def(self):
        """Test building meter definition for Tasmota"""
        # This test requires a valid SML message object
        # We'll test with a mock message if needed
        pass  # Will be implemented when we have valid message objects

if __name__ == "__main__":
    unittest.main()
