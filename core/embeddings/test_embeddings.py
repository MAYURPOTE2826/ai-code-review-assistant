import pytest
from core.embeddings.chunker import CodeChunker
from core.embeddings.embedder import CodeEmbedder

def test_code_chunker_raw_text():
    """
    Tests that the chunker properly splits a long string and respects overlaps.
    """
    chunker = CodeChunker(max_chunk_size=10, overlap=2)
    text = "1234567890abcdefghij" # 20 characters
    
    chunks = chunker.chunk_text(text)
    
    # 1st chunk: "1234567890" (len 10, ends at index 10)
    # Next start = 10 - 2 (overlap) = 8
    # 2nd chunk: "90abcdefgh" (len 10, starts at 8, ends at 18)
    # Next start = 18 - 2 = 16
    # 3rd chunk: "ghij" (starts at 16, ends at 20)
    
    assert len(chunks) == 3
    assert chunks[0]["content"] == "1234567890"
    assert chunks[1]["content"] == "90abcdefgh"
    assert chunks[2]["content"] == "ghij"
    
def test_embedder():
    """
    Tests that the embedder generates vectors of the correct dimension.
    """
    embedder = CodeEmbedder(model_name='all-MiniLM-L6-v2')
    
    test_chunks = [
        {"content": "def hello_world(): print('hello')", "metadata": {}},
        {"content": "class MyModel(BaseModel): pass", "metadata": {}}
    ]
    
    embedded_chunks = embedder.embed_chunks(test_chunks)
    
    assert len(embedded_chunks) == 2
    assert "embedding" in embedded_chunks[0]
    
    # all-MiniLM-L6-v2 generates 384-dimensional vectors
    assert len(embedded_chunks[0]["embedding"]) == 384
    assert isinstance(embedded_chunks[0]["embedding"][0], float)
