import ast
from typing import List, Dict, Any

class ASTExtractor(ast.NodeVisitor):
    """
    Visits the nodes of an Abstract Syntax Tree (AST) to extract meaningful components
    such as classes, functions, and their docstrings.
    
    This is preferred over simple regex text splitting because it understands
    the semantic structure of Python code.
    """
    
    def __init__(self):
        self.classes = []
        self.functions = []
        
    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        """Called when the visitor finds a class definition."""
        class_info = {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "start_line": node.lineno,
            "end_line": node.end_lineno,
            "type": "class"
        }
        self.classes.append(class_info)
        
        # We must call generic_visit to continue searching inside the class (for methods)
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        """Called when the visitor finds a function definition (or method)."""
        function_info = {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "start_line": node.lineno,
            "end_line": node.end_lineno,
            "type": "function"
        }
        self.functions.append(function_info)
        
        # In case there are nested functions
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        """Called for async functions (FastAPI relies heavily on these)."""
        # We can handle them exactly like normal functions for our purposes
        self.visit_FunctionDef(node)


def parse_python_file(file_path: str) -> Dict[str, List[Dict]]:
    """
    Reads a Python file, parses its AST, and extracts classes and functions.
    
    Args:
        file_path (str): The absolute path to the Python file.
        
    Returns:
        Dict: A dictionary containing lists of extracted classes and functions.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        source_code = file.read()
        
    try:
        # Parse the source code into an AST
        tree = ast.parse(source_code)
    except SyntaxError as e:
        # If the file has a syntax error, we can't parse it
        return {"classes": [], "functions": [], "error": str(e)}
        
    # Instantiate our visitor and traverse the tree
    extractor = ASTExtractor()
    extractor.visit(tree)
    
    return {
        "classes": extractor.classes,
        "functions": extractor.functions
    }
