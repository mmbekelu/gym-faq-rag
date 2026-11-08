from app.rag import retrieve
import pytest

def test_retrieve_empty_question():
    with pytest.raises(ValueError):
        retrieve("", 2)

def test_retrieve_invalid_n_results():
    with pytest.raises(ValueError):
        retrieve("When does the gym open?", 0)