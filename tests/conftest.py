"""
tests/conftest.py - Pytest configuration and shared fixtures for all tests
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_oracle_conn():
    """Mock Oracle database connection for testing."""
    conn = Mock()
    conn.cursor.return_value = Mock()
    conn.commit.return_value = None
    conn.rollback.return_value = None
    return conn


@pytest.fixture
def sample_pdf_bytes():
    """Sample PDF binary data for testing file extraction."""
    # This is a minimal PDF structure for testing
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        b"<< /Type /Catalog /Pages 2 0 R >>\n"
        b"endobj\n"
        b"2 0 obj\n"
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
        b"endobj\n"
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\n"
        b"endobj\n"
        b"xref\n"
        b"0 4\n"
        b"0000000000 65535 f\n"
        b"0000000009 00000 n\n"
        b"0000000074 00000 n\n"
        b"0000000133 00000 n\n"
        b"trailer\n"
        b"<< /Size 4 /Root 1 0 R >>\n"
        b"startxref\n"
        b"210\n"
        b"%%EOF\n"
    )


@pytest.fixture
def sample_text():
    """Sample text for chunking tests."""
    return (
        "This is a sample document with multiple sentences. "
        "Each sentence contains words that help test the chunking algorithm. "
        "The quick brown fox jumps over the lazy dog. " * 20  # Repeat to get enough words
    )


@pytest.fixture
def test_env_vars():
    """Set test environment variables."""
    test_vars = {
        "ORA_USER": "test_user",
        "ORA_PASSWORD": "test_pass",
        "ORA_HOST": "localhost",
        "ORA_PORT": "1521",
        "ORA_SERVICE": "TESTDB",
        "ORA_SCHEMA": "DEV",
        "ORA_DOC_TABLE": "TEST_DOCS",
        "ORA_CHUNK_TABLE": "TEST_CHUNKS",
        "VECTOR_TOP_K": "5",
    }
    with patch.dict(os.environ, test_vars):
        yield test_vars
