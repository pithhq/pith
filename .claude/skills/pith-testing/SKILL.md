---
name: pith-testing
description: Testing patterns for PITH — parser tests, config validation, schema validation, and CLI integration tests.
globs: "tests/**/*.py"
---

# PITH Testing Patterns

## Test Structure
```
tests/
  parsers/
    fixtures/           # Sample files for parser tests
      simple.pdf
      simple.docx
      scanned.pdf       # For OCR path testing
    test_pdf_parser.py
    test_docx_parser.py
    test_excel_parser.py
  config/
    test_config_loading.py
    test_config_validation.py
  schema/
    test_schema_loader.py
    test_staleness.py
  cli/
    test_ingest_command.py
    test_query_command.py
    test_lint_command.py
  privacy/
    test_privacy_enforcement.py
```

## Parser Test Pattern
```python
# tests/parsers/test_pdf_parser.py
import pytest
from pathlib import Path
from pith.parsers.pdf import PdfParser

FIXTURES = Path(__file__).parent / "fixtures"

class TestPdfParser:
    def test_supports_pdf_extension(self):
        parser = PdfParser()
        assert parser.supports(Path("document.pdf"))
        assert parser.supports(Path("DOCUMENT.PDF"))
        assert not parser.supports(Path("document.docx"))
    
    def test_extracts_text_from_text_pdf(self):
        parser = PdfParser()
        result = parser.parse(FIXTURES / "simple.pdf")
        assert result.content
        assert "expected content" in result.content
        assert result.requires_ocr is False
    
    def test_returns_empty_content_for_scanned_pdf(self):
        parser = PdfParser()
        result = parser.parse(FIXTURES / "scanned.pdf")
        assert result.content == ""
        assert result.requires_ocr is True
        # Does NOT raise — graceful degradation
    
    def test_counts_pages_correctly(self):
        parser = PdfParser()
        result = parser.parse(FIXTURES / "multipage.pdf")
        assert result.page_count == 3
```

## Privacy Enforcement Tests
```python
# tests/privacy/test_privacy_enforcement.py
import pytest
from pith.privacy import can_send_to_cloud_model, PrivacyViolationError
from pith.models import Client

class TestPrivacyEnforcement:
    def test_level_1_blocks_cloud_model(self):
        client = Client(id="test-client", privacy_level=1)
        with pytest.raises(PrivacyViolationError) as exc_info:
            can_send_to_cloud_model("sensitive content", client)
        assert "Level 1" in str(exc_info.value)
        assert "local-only" in str(exc_info.value)
    
    def test_level_2_allows_cloud_model(self):
        client = Client(id="test-client", privacy_level=2)
        # Should not raise
        result = can_send_to_cloud_model("content", client)
        assert result is True
    
    def test_level_1_excludes_from_global_graph(self):
        from pith.privacy import can_include_in_global_query
        client = Client(id="test-client", privacy_level=1)
        entity = WikiEntity(entity_id="test", client_id="test-client")
        assert can_include_in_global_query(entity, client) is False
```

## CLI Integration Tests
```python
# tests/cli/test_ingest_command.py
import pytest
from typer.testing import CliRunner
from pathlib import Path
from pith.cli import app

runner = CliRunner()

class TestIngestCommand:
    def test_ingest_existing_file(self, tmp_path):
        # Create a test wiki
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        config = create_test_config(wiki_root=wiki_dir)
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content for ingestion")
        
        result = runner.invoke(app, ["ingest", str(test_file)])
        assert result.exit_code == 0
        assert "Ingested" in result.output
    
    def test_ingest_nonexistent_file_fails_gracefully(self, tmp_path):
        result = runner.invoke(app, ["ingest", "/nonexistent/file.pdf"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower()
    
    def test_ingest_json_output_is_valid(self, tmp_path):
        import json
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")
        
        result = runner.invoke(app, ["ingest", str(test_file), "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "pages_created" in data
        assert "pages_updated" in data
```

## Running Tests
```bash
# All tests with coverage
pytest --cov=pith --cov-report=term-missing

# Specific module
pytest tests/parsers/ -v

# Fast (skip integration tests that need API)
pytest -m "not integration" -v

# With output (useful for debugging)
pytest -s tests/privacy/
```
