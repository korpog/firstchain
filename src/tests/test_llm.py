# tests/test_llm.py
from unittest.mock import Mock, patch
import pytest
from app.llm import load_split_text, build_graph, setup_llm

@pytest.fixture
def mock_text_loader():
    with patch("llm.TextLoader") as mock:
        mock.return_value.load.return_value = [Mock(page_content="test content")]
        yield mock

@pytest.fixture
def mock_text_splitter():
    with patch("llm.RecursiveCharacterTextSplitter") as mock:
        mock.return_value.split_documents.return_value = [
            Mock(page_content="split content 1"),
            Mock(page_content="split content 2")
        ]
        yield mock

def test_load_split_text(mock_text_loader, mock_text_splitter):
    result = load_split_text("test.txt")
    assert len(result) == 2
    assert result[0].page_content == "split content 1"
    assert result[1].page_content == "split content 2"

@patch("llm.ChatOllama")
@patch("llm.Chroma")
def test_build_graph(mock_chroma, mock_chat_ollama):
    mock_vector_store = Mock()
    mock_llm = Mock()
    
    graph = build_graph(mock_vector_store, mock_llm)
    assert graph is not None
    # Add more specific assertions based on your graph structure

@patch("llm.ChatOllama")
@patch("llm.OllamaEmbeddings")
@patch("llm.Chroma")
def test_setup_llm(mock_chroma, mock_embeddings, mock_chat_ollama):
    with patch("llm.load_split_text") as mock_load_split:
        mock_load_split.return_value = [Mock(page_content="test content")]
        graph = setup_llm()
        assert graph is not None
        # Add more specific assertions based on your graph structure