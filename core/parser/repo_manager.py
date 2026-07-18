import os
import shutil
from pathlib import Path
from git import Repo, GitCommandError
import logging

logger = logging.getLogger(__name__)

class RepositoryManager:
    """
    Manages the ingestion of source code repositories.
    Currently supports cloning from a Git URL.
    """
    
    def __init__(self, base_storage_path: str = "./data/repos"):
        """
        Args:
            base_storage_path (str): The root directory where repositories will be cloned.
        """
        self.base_storage_path = Path(base_storage_path)
        self.base_storage_path.mkdir(parents=True, exist_ok=True)

    def clone_repository(self, repo_url: str, repo_name: str) -> str:
        """
        Clones a repository from a URL into the local storage.
        If the repo already exists, it can be updated or skipped.
        
        Args:
            repo_url (str): The Git URL (e.g., https://github.com/user/repo.git)
            repo_name (str): A unique name for the repository folder.
            
        Returns:
            str: The absolute path to the cloned repository.
        """
        target_path = self.base_storage_path / repo_name
        
        if target_path.exists():
            logger.info(f"Repository {repo_name} already exists at {target_path}. Skipping clone.")
            # In a production scenario, we might want to do `git pull` here instead.
            return str(target_path.absolute())
            
        logger.info(f"Cloning {repo_url} into {target_path}...")
        try:
            Repo.clone_from(repo_url, target_path)
            logger.info("Clone successful.")
            return str(target_path.absolute())
        except GitCommandError as e:
            logger.error(f"Failed to clone repository: {e}")
            raise

    def get_python_files(self, repo_path: str) -> list[str]:
        """
        Recursively finds all Python (.py) files in the repository.
        Ignores virtual environments and hidden folders.
        
        Args:
            repo_path (str): The path to the local repository.
            
        Returns:
            list[str]: A list of absolute file paths to Python files.
        """
        python_files = []
        path = Path(repo_path)
        
        for file in path.rglob("*.py"):
            # Skip common non-project directories
            if any(part.startswith('.') or part in ['venv', 'env', '__pycache__', 'node_modules'] for part in file.parts):
                continue
            python_files.append(str(file.absolute()))
            
        return python_files
