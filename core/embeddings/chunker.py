import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class CodeChunker:
    """
    Splits large code files and AST nodes into smaller, semantically meaningful chunks.
    This is necessary because LLMs and embedding models have context window limits.
    """
    
    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        """
        Args:
            max_chunk_size (int): The maximum number of characters in a single chunk.
            overlap (int): The number of characters to overlap between chunks to maintain context.
        """
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, metadata: dict = None) -> List[Dict]:
        """
        Splits a raw string of text into overlapping chunks.
        
        Args:
            text (str): The raw text to split.
            metadata (dict): Metadata to attach to each chunk (e.g., file path).
            
        Returns:
            List[Dict]: A list of chunk dictionaries.
        """
        if not text:
            return []
            
        metadata = metadata or {}
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + self.max_chunk_size, text_length)
            
            # If we're not at the very end, try to find a newline to break cleanly
            if end < text_length:
                # Look backwards for a newline in the last 10% of the chunk
                search_start = max(start, end - int(self.max_chunk_size * 0.1))
                last_newline = text.rfind('\n', search_start, end)
                if last_newline != -1:
                    end = last_newline + 1 # Include the newline
            
            chunk_content = text[start:end]
            chunks.append({
                "content": chunk_content,
                "metadata": {**metadata, "start_char": start, "end_char": end}
            })
            
            # Move the start forward, subtracting overlap
            start = end - self.overlap
            
            # Prevent infinite loops if overlap is bigger than progression
            if start <= chunks[-1]["metadata"]["start_char"]:
                start = chunks[-1]["metadata"]["end_char"]
                
        return chunks

    def chunk_ast_nodes(self, file_path: str, ast_results: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Creates chunks directly from the AST extraction results.
        This ensures that a whole function or class is kept together as a single chunk 
        if possible, which is vastly superior for semantic search.
        
        Args:
            file_path (str): The path to the file.
            ast_results (Dict): The results from our ASTExtractor.
            
        Returns:
            List[Dict]: A list of semantically rich chunks.
        """
        chunks = []
        
        # Read the original file to get the exact text for the nodes
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            logger.error(f"Failed to read {file_path} for chunking: {e}")
            return chunks

        # Process classes
        for cls in ast_results.get("classes", []):
            start = cls["start_line"] - 1 # 0-indexed
            end = cls["end_line"]
            content = "".join(lines[start:end])
            
            # If a class is massive, we fallback to raw text chunking
            if len(content) > self.max_chunk_size * 2:
                 sub_chunks = self.chunk_text(content, metadata={"file": file_path, "type": "class", "name": cls["name"]})
                 chunks.extend(sub_chunks)
            else:
                chunks.append({
                    "content": content,
                    "metadata": {"file": file_path, "type": "class", "name": cls["name"], "start_line": cls["start_line"], "end_line": cls["end_line"]}
                })

        # Process functions
        for func in ast_results.get("functions", []):
            start = func["start_line"] - 1
            end = func["end_line"]
            content = "".join(lines[start:end])
            
            if len(content) > self.max_chunk_size * 2:
                 sub_chunks = self.chunk_text(content, metadata={"file": file_path, "type": "function", "name": func["name"]})
                 chunks.extend(sub_chunks)
            else:
                chunks.append({
                    "content": content,
                    "metadata": {"file": file_path, "type": "function", "name": func["name"], "start_line": func["start_line"], "end_line": func["end_line"]}
                })
                
        return chunks
