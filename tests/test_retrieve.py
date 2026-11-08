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
    data=[SimpleNamespace(embedding=[0.1, 0.2, 0.3])]
)



# person = SimpleNamespace(
#     hobbies=[SimpleNamespace(name="reading")]
# )

# print(person.hobbies[0].name)
