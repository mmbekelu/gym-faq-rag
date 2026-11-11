from app.rag import retrieve
import pytest
from types import SimpleNamespace

def test_retrieve_empty_question():
    with pytest.raises(ValueError):
        retrieve("", 2)

def test_retrieve_invalid_n_results():
    with pytest.raises(ValueError):
        retrieve("When does the gym open?", 0)


def test_retrieve_returns_documents(monkeypatch):
    fake_response = SimpleNamespace(
        data=[SimpleNamespace(embedding=[0.1, 0.2, 0.3])],
        model="text-embedding-3-small",
        usage=SimpleNamespace(total_tokens=5),
        _request_id="fake-request-123"
    )

    def fake_create(model, input):
        return fake_response

    monkeypatch.setattr(
        "app.rag.client.embeddings.create",
        fake_create
    )

    fake_results = {
    "documents": [
        ["FAQ about opening hours", "FAQ about guest passes"]
    ],
    "ids": [
        ["faq-1", "faq-2"]
    ],
    "distances": [
        [0.12, 0.25]
    ]
    }

    def fake_query(query_embeddings, n_results, include):
        return fake_results

    fake_collection = SimpleNamespace(query=fake_query)

    def fake_get_collection(name):
        return fake_collection

    fake_chroma_client = SimpleNamespace(get_collection=fake_get_collection)

    def fake_persistent_client(path):
        return fake_chroma_client
    
    monkeypatch.setattr(
    "app.rag.chromadb.PersistentClient",
    fake_persistent_client
    )

    result = retrieve("When does the gym open?", 2)

    assert result[0] == ["FAQ about opening hours", "FAQ about guest passes"]
    assert result[1] == ["faq-1", "faq-2"]