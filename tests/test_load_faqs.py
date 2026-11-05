from app.rag import load_faqs
import pytest

def test_load_faqs(tmp_path):
    faq_file = tmp_path / "sample_faq.txt"

    faq_file.write_text("Welcome to the gym!", encoding="utf-8")
    actual = load_faqs(faq_file)

    assert actual == "Welcome to the gym!"

def test_empty_faq_file(tmp_path):
    faq_file = tmp_path / "empty_faq.txt"

    faq_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError):
        load_faqs(faq_file)

def test_whitespace_faq_file(tmp_path):
    faq_file = tmp_path / "test_whitespace_faq.txt"
    faq_file.write_text("  ", encoding="utf-8")
    with pytest.raises(ValueError):
        load_faqs(faq_file)

def test_missing_faq_file(tmp_path):
    faq_file = tmp_path / "missing_faq.txt"

    with pytest.raises(FileNotFoundError):
        load_faqs(faq_file)