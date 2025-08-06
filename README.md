# tasmota-sml-parser
Webapp to conveniently parse Tasmota SML Dump output and display the actual data contained.

Makes building a Tasmota SML Script much easier.

Online Demo is at https://tasmota-sml-parser.dicp.net/.

## Development

### Requirements
- Python 3.9 - 3.13
- Flask
- smllib

### Installation
```bash
# Clone repository
git clone https://github.com/ixs/tasmota-sml-parser.git
cd tasmota-sml-parser

# Create virtual environment
make venv

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
python app.py
```

The application will be available at http://localhost:5000

## Testing

This project includes comprehensive unit, integration, and functional tests.

### Quick Start
```bash
# Run all tests
make test

# Run only unit tests
make test-unit

# Run with coverage report
make test-coverage
```

### Test Structure
- `tests/test_sml_decoder.py` - Unit tests for SML decoder
- `tests/test_app.py` - Functional tests for Flask app  
- `tests/test_integration.py` - Integration tests
- `tests/test_performance.py` - Performance and stress tests

For detailed testing information, see [tests/README.md](tests/README.md).

### Available Make Targets
```bash
make test              # Run all tests
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-functional   # Functional tests only
make test-performance  # Performance tests
make test-coverage     # Tests with coverage report
make test-lint         # Code linting
make test-quick        # Quick tests without dependencies
make clean-test        # Clean test artifacts
```
