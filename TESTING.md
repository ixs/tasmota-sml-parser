# Tasmota SML Parser - Test Suite

Dieses Repository enthält eine umfassende Test-Suite für den Tasmota SML Parser.

## Zusammenfassung

✅ **Unit Tests**: 15+ Tests für SML Decoder-Funktionalität  
✅ **Funktionale Tests**: 10+ Tests für Flask-App  
✅ **Integrationstests**: End-to-End Workflow Tests  
✅ **Performance Tests**: Stress- und Speicher-Tests  
✅ **CI/CD Integration**: GitHub Actions Workflows  

## Python-Versionskompatibilität

| Branch | Python-Versionen | Status |
|--------|------------------|--------|
| `master` | 3.9 - 3.13 | ✅ Vollständig unterstützt |

## Schnellstart

```bash
# Tests ausführen
make test

# Spezifische Test-Kategorien
make test-unit          # Unit Tests
make test-functional    # Funktionale Tests  
make test-integration   # Integrationstests
make test-performance   # Performance Tests

# Mit Coverage
make test-coverage
```

## Test-Kategorien

### 1. Unit Tests (`tests/test_sml_decoder*.py`)
- **Parser Input Validation**: Verschiedene SML Input-Formate
- **Frame Decoding**: SML Frame-Verarbeitung mit echten Testdaten
- **Error Handling**: Robuste Fehlerbehandlung
- **OBIS Code Processing**: Korrekte OBIS-Code-Verarbeitung
- **Edge Cases**: Grenzfälle und ungewöhnliche Eingaben

**Testdaten**: Echte SML-Nachrichten aus `test-data.txt`

### 2. Funktionale Tests (`tests/test_app*.py`)
- **HTTP Routes**: GET/POST Endpunkte
- **Form Processing**: SML Dump Formular-Verarbeitung
- **Template Rendering**: HTML-Ausgabe Validierung
- **Error Pages**: Fehlerseiten-Handling
- **JSON Responses**: API-Response Validierung

**Mock-Strategien**: Flask Test Client, SML Parser Mocking

### 3. Integrationstests (`tests/test_integration.py`)
- **End-to-End Workflow**: Vollständiger Parsing-Prozess
- **File Operations**: Datei-basierte Verarbeitung
- **Error Recovery**: Fehler-Resilience
- **Real Data Processing**: Verarbeitung echter SML-Daten

### 4. Performance Tests (`tests/test_performance.py`)
- **Large Dataset Processing**: 1000+ SML-Nachrichten
- **Memory Usage**: Speicherverbrauch-Monitoring
- **Concurrency**: Gleichzeitige Request-Verarbeitung
- **Stress Testing**: Edge-Case Belastungstests

## CI/CD Integration

### GitHub Actions Workflows

**Master Branch** (`.github/workflows/tests.yml`):
- Python 3.9 - 3.13 Matrix
- Vollständige Test-Suite
- Coverage Reports
- Performance Tests

### Test-Metriken

- **Code Coverage**: Ziel >90%
- **Test Execution Time**: <30 Sekunden (ohne Performance Tests)
- **Performance Benchmarks**: 
  - 1000 SML-Nachrichten in <10 Sekunden
  - Memory Usage <100MB Increase

## Best Practices
- **Test Execution Time**: <30 Sekunden (ohne Performance Tests)
- **Performance Benchmarks**: 
  - 1000 SML-Nachrichten in <10 Sekunden
  - Memory Usage <100MB Increase

## Best Practices

### Test-Entwicklung
1. **Realistische Testdaten**: Echte SML-Nachrichten verwenden
2. **Isolated Tests**: Jeder Test ist unabhängig
3. **Clear Naming**: Aussagekräftige Testfunktions-Namen
4. **Comprehensive Coverage**: Happy Path + Edge Cases

### Performance
1. **Marked Slow Tests**: Performance Tests mit `@pytest.mark.slow`
2. **Memory Monitoring**: psutil für Speicherverbrauch
3. **Timeout Protection**: Zeitlimits für lange Tests

### Error Handling
1. **Graceful Degradation**: Tests sollten bei Fehlern nicht abstürzen
2. **Error Collection**: Parse-Fehler sammeln statt Exception werfen
3. **Recovery Testing**: Tests für Fehler-Recovery

## Wartung

### Regelmäßige Aufgaben
- [ ] Test-Daten aktualisieren bei neuen SML-Formaten
- [ ] Performance-Benchmarks überprüfen
- [ ] Dependencies aktualisieren (`requirements-test.txt`)
- [ ] Coverage-Ziele anpassen

### Bei Änderungen
- [ ] Unit Tests für neue Funktionen
- [ ] Integration Tests für neue Workflows
- [ ] Performance Tests bei Algorithmus-Änderungen
- [ ] Documentation Updates

## Troubleshooting

### Häufige Probleme

**Import Errors in Tests**:
```bash
# Tests im falschen Verzeichnis
cd /workspaces/tasmota-sml-parser
python -m pytest tests/
```

**Python Version Conflicts**:
```bash
# Check current version
python --version

# Supported versions: Python 3.9 - 3.13
```

**Missing Dependencies**:
```bash
pip install -r requirements-test.txt
```

**Performance Test Failures**:
```bash
# Skip slow tests
pytest tests/ -m "not slow"
```

## Contribution Guidelines

Beim Hinzufügen neuer Tests:

1. **Kategorisierung**: Richtige Test-Kategorie wählen
2. **Documentation**: Docstrings für Test-Zweck
3. **Data**: Realistische Testdaten verwenden
4. **Performance**: Slow Tests markieren
5. **CI/CD**: Tests müssen in GitHub Actions laufen

## Support

Bei Problemen mit den Tests:
1. Dokumentation in `tests/README.md` prüfen
2. GitHub Issues für Test-spezifische Probleme
3. CI/CD Logs für Debugging-Information

## Branch Information

- **Branch**: `feature/comprehensive-test-suite`
- **Base**: `master` 
- **Ready for**: Review, testing, and iteration
- **Compatible with**: Python 3.9 - 3.13

The implementation follows Python testing best practices and provides a solid foundation for maintaining code quality as the application evolves. All tests are designed to be maintainable, readable, and provide meaningful feedback when issues occur.
