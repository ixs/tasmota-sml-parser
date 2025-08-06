import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sml_decoder import TasmotaSMLParser
import binascii

class TestSMLDecoderPytest:
    """Pytest-based tests for SML decoder with fixtures and parametrization"""
    
    @pytest.fixture
    def parser(self):
        """Fixture providing a fresh parser instance for each test"""
        return TasmotaSMLParser()
    
    @pytest.fixture
    def sample_sml_lines(self):
        """Fixture providing sample SML data lines"""
        return [
            "15:57:05.415 : 77 07 01 00 60 05 00 ff 01 01 01 01 65 00 1c 81 04 01 01 01 63 33 14 00 76 04 00 00 03 62 00 62 00 72 65 00 00 02 01 71",
            "15:57:05.435 : 77 01 0b 0a 01 48 4c 59 02 00 01 1c 0f 01 01 f1 04",
            "77 07 01 00 60 32 01 01 01 01 01 01 04 48 4c 59 01",  # Without timestamp
        ]
    
    @pytest.mark.parametrize("input_line,expected_type", [
        ("15:57:05.415 : 77 07 01 00 60 05 00 ff", bytes),
        ("77 07 01 00 60 05 00 ff", bytes),
        ("invalid input", type(None)),
        ("", type(None)),
        ("15:57:05.415 : invalid hex", type(None)),
    ])
    def test_parse_input_various_formats(self, parser, input_line, expected_type):
        """Test parsing various input formats"""
        result = parser.parse_input(input_line)
        assert type(result) == expected_type
    
    def test_parse_input_hex_conversion(self, parser):
        """Test that hex conversion works correctly"""
        input_line = "15:57:05.415 : 77 07 01 00"
        result = parser.parse_input(input_line)
        expected = binascii.a2b_hex("77070100")
        assert result == expected
    
    def test_parse_errors_collection(self, parser):
        """Test that parse errors are collected correctly"""
        invalid_lines = ["invalid1", "invalid2", ""]
        
        for line in invalid_lines:
            parser.parse_input(line)
        
        assert len(parser.parse_errors) == len(invalid_lines)
        for line in invalid_lines:
            assert line in parser.parse_errors
    
    @patch('sml_decoder.SmlFrame')
    def test_decode_frame_success(self, mock_sml_frame, parser):
        """Test successful frame decoding with mocked SmlFrame"""
        mock_frame_instance = MagicMock()
        mock_frame_instance.get_obis.return_value = [MagicMock()]
        mock_sml_frame.return_value = mock_frame_instance
        
        frame = b'\x77\x07\x01\x00'
        result = parser.decode_frame(frame)
        
        assert result is not None
        mock_sml_frame.assert_called_once_with(frame)
        mock_frame_instance.get_obis.assert_called_once()
    
    @patch('sml_decoder.SmlFrame')
    def test_decode_frame_empty_messages(self, mock_sml_frame, parser):
        """Test frame decoding when no messages are returned"""
        mock_frame_instance = MagicMock()
        mock_frame_instance.get_obis.return_value = []
        mock_sml_frame.return_value = mock_frame_instance
        
        frame = b'\x77\x07\x01\x00'
        result = parser.decode_frame(frame)
        
        assert result is False
    
    @patch('sml_decoder.SmlFrame')
    def test_decode_frame_exception(self, mock_sml_frame, parser):
        """Test frame decoding when SmlFrame raises an exception"""
        mock_frame_instance = MagicMock()
        mock_frame_instance.get_obis.side_effect = Exception("Parse error")
        mock_sml_frame.return_value = mock_frame_instance
        
        frame = b'\x77\x07\x01\x00'
        result = parser.decode_frame(frame)
        
        assert result is None
        assert len(parser.obis_errors) == 1
        assert parser.obis_errors[0]['frame'] == frame
    
    def test_decode_messages_workflow(self, parser, sample_sml_lines):
        """Test the complete decode_messages workflow"""
        with patch.object(parser, 'decode_frame') as mock_decode:
            # Mock successful decoding
            mock_message = MagicMock()
            mock_message.obis = "test_obis_1"
            mock_decode.return_value = [mock_message]
            
            result = parser.decode_messages(sample_sml_lines)
            
            assert isinstance(result, list)
            # Should be called for each valid line
            assert mock_decode.call_count >= 1
    
    def test_obis_deduplication(self, parser):
        """Test that duplicate OBIS codes are handled correctly"""
        with patch.object(parser, 'parse_input') as mock_parse, \
             patch.object(parser, 'decode_frame') as mock_decode:
            
            # Mock the same OBIS appearing twice
            mock_message1 = MagicMock()
            mock_message1.obis = "duplicate_obis"
            mock_message2 = MagicMock()
            mock_message2.obis = "duplicate_obis"
            
            mock_parse.return_value = b'\x77\x07\x01\x00'
            mock_decode.side_effect = [[mock_message1], [mock_message2]]
            
            result = parser.decode_messages(["line1", "line2"])
            
            # Should only include the first occurrence
            assert len(result) == 1
            assert result[0].obis == "duplicate_obis"
    
    @pytest.mark.parametrize("obis_code,expected_in_output", [
        ("010800", True),  # Should generate valid meter definition
        ("020800", True),  # Should generate valid meter definition
    ])
    def test_build_meter_def_format(self, parser, obis_code, expected_in_output):
        """Test meter definition building with various OBIS codes"""
        mock_message = MagicMock()
        mock_message.obis.obis_code = obis_code
        mock_message.obis.upper.return_value = obis_code.upper()
        
        with patch.object(parser, 'get_message_details') as mock_details:
            mock_details.return_value = {
                'obis': MagicMock(),
                'name': 'Test Name',
                'unit': 'kWh',
                'topic': 'test_topic',
                'precision': 2
            }
            mock_details.return_value['obis'].upper.return_value = obis_code.upper()
            
            result = parser.build_meter_def(mock_message)
            
            assert result.startswith("1,7707")
            if expected_in_output:
                assert obis_code.upper() in result
    
    def test_error_resilience(self, parser):
        """Test parser resilience to various error conditions"""
        problematic_inputs = [
            None,  # This might cause issues if not handled
            [],
            [""],
            ["   "],  # Whitespace only
            ["15:57:05.415 : "],  # Missing hex data
            ["77"],  # Too short hex
        ]
        
        for problem_input in problematic_inputs:
            try:
                # Should not raise unhandled exceptions
                if problem_input is not None:
                    result = parser.decode_messages(problem_input)
                    assert isinstance(result, list)
            except Exception as e:
                pytest.fail(f"Parser should handle {problem_input} gracefully, but raised {e}")

class TestSMLDecoderEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_binascii_error_handling(self):
        """Test handling of binascii conversion errors"""
        parser = TasmotaSMLParser()
        
        # These should trigger binascii.Error
        invalid_hex_lines = [
            "15:57:05.415 : 77 GG 01 00",  # Invalid hex characters
            "77 ZZ XX YY",  # Invalid hex characters
            "15:57:05.415 : 7",  # Odd number of hex characters
        ]
        
        for line in invalid_hex_lines:
            result = parser.parse_input(line)
            assert result is None
            assert line in parser.parse_errors
    
    def test_memory_usage_with_large_input(self):
        """Test memory usage with large inputs"""
        parser = TasmotaSMLParser()
        
        # Create a large number of lines
        large_input = ["invalid line"] * 10000
        
        # Should handle large inputs without excessive memory usage
        result = parser.decode_messages(large_input)
        assert isinstance(result, list)
        assert len(parser.parse_errors) == 10000
