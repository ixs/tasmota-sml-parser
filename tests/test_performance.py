import pytest
import time
from unittest.mock import patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sml_decoder import TasmotaSMLParser
from app import app

class TestPerformance:
    """Performance tests for SML parser"""
    
    @pytest.fixture
    def parser(self):
        return TasmotaSMLParser()
    
    @pytest.fixture
    def large_dataset(self):
        """Generate a large dataset for performance testing"""
        base_line = "15:57:05.415 : 77 07 01 00 60 05 00 ff 01 01 01 01 65 00 1c 81 04 01 01 01 63 33 14 00 76 04 00 00 03 62 00 62 00 72 65 00 00 02 01 71"
        return [base_line] * 1000
    
    @pytest.mark.slow
    def test_large_input_parsing_performance(self, parser, large_dataset):
        """Test performance with large input dataset"""
        start_time = time.time()
        
        messages = parser.decode_messages(large_dataset)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert duration < 10.0, f"Parsing took {duration} seconds, which is too slow"
        assert isinstance(messages, list)
    
    @pytest.mark.slow
    def test_memory_usage_large_dataset(self, parser):
        """Test memory usage with large dataset"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate large dataset
        large_data = ["invalid line"] * 10000
        parser.decode_messages(large_data)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Should not increase memory by more than 100MB (adjust as needed)
        assert memory_increase < 100, f"Memory increased by {memory_increase}MB"
    
    @pytest.mark.slow
    def test_flask_app_performance(self, large_dataset):
        """Test Flask app performance with large dataset"""
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            large_sml_dump = '\n'.join(large_dataset)
            
            start_time = time.time()
            
            response = client.post('/decode', data={'smldump': large_sml_dump})
            
            end_time = time.time()
            duration = end_time - start_time
            
            assert response.status_code == 200
            # Should complete within reasonable time
            assert duration < 15.0, f"Request took {duration} seconds"

class TestConcurrency:
    """Concurrency tests for the application"""
    
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_multiple_simultaneous_requests(self, client):
        """Test handling multiple simultaneous requests"""
        import threading
        import queue
        
        results = queue.Queue()
        sample_data = "15:57:05.415 : 77 07 01 00 60 05 00 ff"
        
        def make_request():
            response = client.post('/decode', data={'smldump': sample_data})
            results.put(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            t = threading.Thread(target=make_request)
            threads.append(t)
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Check results
        status_codes = []
        while not results.empty():
            status_codes.append(results.get())
        
        assert len(status_codes) == 5
        assert all(code == 200 for code in status_codes)

class TestStress:
    """Stress tests for edge cases"""
    
    def test_very_long_input_lines(self):
        """Test with very long input lines"""
        parser = TasmotaSMLParser()
        
        # Create very long hex string
        long_hex = "77 " + "00 " * 10000
        very_long_line = f"15:57:05.415 : {long_hex}"
        
        # Should handle without crashing
        result = parser.parse_input(very_long_line)
        # Might be None due to invalid format, but should not crash
        assert result is None or isinstance(result, bytes)
    
    def test_malformed_timestamps(self):
        """Test with various malformed timestamp formats"""
        parser = TasmotaSMLParser()
        
        malformed_timestamps = [
            "not_a_time : 77 07 01 00",
            "25:99:99.999 : 77 07 01 00",
            ": 77 07 01 00",  # Missing timestamp
            "77 07 01 00 :",  # Reversed format
        ]
        
        for line in malformed_timestamps:
            result = parser.parse_input(line)
            # Should handle gracefully
            assert result is None or isinstance(result, bytes)
    
    def test_unicode_and_encoding_issues(self):
        """Test with unicode and encoding edge cases"""
        parser = TasmotaSMLParser()
        
        unicode_inputs = [
            "15:57:05.415 : 77 07 01 00 café",  # Unicode in hex area
            "🕐 : 77 07 01 00",  # Unicode timestamp
            "15:57:05.415 : 77 07 01 00 ñ",  # Non-ASCII character
        ]
        
        for line in unicode_inputs:
            try:
                result = parser.parse_input(line)
                # Should not crash, result can be None
                assert result is None or isinstance(result, bytes)
            except UnicodeError:
                # Unicode errors are acceptable for malformed input
                pass

class TestErrorRecovery:
    """Test error recovery and resilience"""
    
    def test_parser_state_after_errors(self):
        """Test that parser maintains consistent state after errors"""
        parser = TasmotaSMLParser()
        
        # Process some invalid data
        invalid_data = ["invalid1", "invalid2", "invalid3"]
        parser.decode_messages(invalid_data)
        
        # Check that error lists are populated
        assert len(parser.parse_errors) > 0
        
        # Now process valid data - should still work
        valid_data = ["77 07 01 00 60 05 00 ff"]
        result = parser.decode_messages(valid_data)
        
        # Should still be able to process data
        assert isinstance(result, list)
    
    def test_partial_hex_recovery(self):
        """Test recovery from partial hex data"""
        parser = TasmotaSMLParser()
        
        partial_hex_lines = [
            "15:57:05.415 : 77 07 01",  # Incomplete
            "15:57:05.415 : 77 07",     # Very incomplete
            "15:57:05.415 : 77",       # Minimal
        ]
        
        for line in partial_hex_lines:
            result = parser.parse_input(line)
            # Should handle gracefully
            assert result is None or isinstance(result, bytes)
