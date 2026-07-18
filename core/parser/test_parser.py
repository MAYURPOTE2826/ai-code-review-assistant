import pytest
import os
import tempfile
from core.parser.ast_extractor import parse_python_file
from core.parser.repo_manager import RepositoryManager

def test_ast_extractor():
    """
    Tests that our AST extractor can properly identify classes and functions
    from a raw Python file string.
    """
    # We create a temporary python file to parse
    test_code = """
class MyTestClass:
    '''This is a class docstring.'''
    
    def my_method(self):
        pass

def my_function():
    '''This is a function docstring.'''
    return True
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp:
        temp.write(test_code)
        temp_path = temp.name
        
    try:
        results = parse_python_file(temp_path)
        
        # Check classes
        assert len(results["classes"]) == 1
        assert results["classes"][0]["name"] == "MyTestClass"
        assert results["classes"][0]["docstring"] == "This is a class docstring."
        
        # Check functions
        # There are 2: my_method and my_function
        assert len(results["functions"]) == 2
        func_names = [f["name"] for f in results["functions"]]
        assert "my_method" in func_names
        assert "my_function" in func_names
        
    finally:
        os.remove(temp_path)

def test_repo_manager_get_files():
    """
    Tests that the repo manager correctly identifies Python files in a directory.
    """
    manager = RepositoryManager(base_storage_path="./test_data")
    
    # Create dummy structure
    os.makedirs("./test_data/dummy_repo/venv", exist_ok=True)
    
    with open("./test_data/dummy_repo/main.py", "w") as f:
        f.write("print('hello')")
        
    with open("./test_data/dummy_repo/venv/ignore_me.py", "w") as f:
        f.write("print('ignore')")
        
    try:
        files = manager.get_python_files("./test_data/dummy_repo")
        assert len(files) == 1
        assert files[0].endswith("main.py")
    finally:
        import shutil
        shutil.rmtree("./test_data")
