import pytest
import os
import shutil
from core.vector_store.chroma_db import VectorStore

@pytest.fixture
def test_vector_store():
    """
    Creates a temporary ChromaDB instance for testing.
    """
    db_path = "./test_chroma_db"
    store = VectorStore(db_path=db_path)
    yield store
    # Cleanup after test
    if os.path.exists(db_path):
        shutil.rmtree(db_path, ignore_errors=True)

def test_insert_and_search(test_vector_store):
    """
    Tests that we can insert chunks with embeddings and retrieve them 
    using a similar query embedding.
    """
    repo_id = "test_repo_1"
    
    # Let's pretend our embedder generated these 3-dimensional vectors for simplicity.
    # In reality, they are 384-dimensional.
    chunk1 = {
        "content": "def add(a, b): return a + b",
        "metadata": {"type": "function", "name": "add"},
        "embedding": [1.0, 0.0, 0.0]  # Completely represents X
    }
    chunk2 = {
        "content": "def get_user_from_db(): pass",
        "metadata": {"type": "function", "name": "get_user_from_db"},
        "embedding": [0.0, 1.0, 0.0]  # Completely represents Y
    }
    
    test_vector_store.insert_chunks(repo_id, [chunk1, chunk2])
    
    # Pretend the user asked: "Where is the math addition function?"
    # The embedder would turn that question into a vector close to chunk1's vector.
    query_embedding = [0.9, 0.1, 0.0] 
    
    results = test_vector_store.semantic_search(repo_id, query_embedding, n_results=1)
    
    assert len(results) == 1
    assert results[0]["content"] == "def add(a, b): return a + b"
    assert results[0]["metadata"]["name"] == "add"
    
    # Test that the distance is calculated (closer to 0 is better)
    assert "distance" in results[0]
