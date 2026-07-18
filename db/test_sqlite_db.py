import pytest
import os
from db.sqlite_db import DatabaseManager

@pytest.fixture
def db_manager():
    """
    Fixture to create a temporary database for testing, ensuring tests 
    don't pollute the production database.
    """
    test_db_path = "test_codeinsight.db"
    db = DatabaseManager(test_db_path)
    yield db
    # Cleanup after test
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

def test_insert_and_get_repository(db_manager):
    """
    Test that we can insert a repository and retrieve it correctly.
    """
    repo_name = "test-repo"
    local_path = "/tmp/test-repo"
    
    # Insert
    repo_id = db_manager.insert_repository(name=repo_name, local_path=local_path)
    assert repo_id is not None
    assert isinstance(repo_id, int)
    
    # Retrieve
    repo = db_manager.get_repository(repo_id)
    assert repo is not None
    assert repo["name"] == repo_name
    assert repo["local_path"] == local_path
    assert repo["url"] is None
