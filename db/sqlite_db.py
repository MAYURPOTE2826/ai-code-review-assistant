import sqlite3
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages the SQLite database connection and provides methods for data persistence.
    
    This follows the Repository Pattern, separating the data access logic from the
    business logic of the application.
    """

    def __init__(self, db_path: str = "codeinsight.db"):
        """
        Initializes the database connection and creates tables if they don't exist.
        
        Args:
            db_path (str): The path to the SQLite database file.
        """
        # Ensure the directory exists if the db_path includes folders
        db_dir = Path(db_path).parent
        if db_dir.name and db_dir.name != '.':
            db_dir.mkdir(parents=True, exist_ok=True)
            
        self.db_path = db_path
        self._initialize_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """
        Establishes a connection to the SQLite database.
        Uses context managers (via 'with') to ensure proper closure by the caller.
        
        Returns:
            sqlite3.Connection: The database connection object.
        """
        conn = sqlite3.connect(self.db_path)
        # Row factory allows us to access columns by name (dict-like)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_schema(self) -> None:
        """
        Creates the foundational schema for CodeInsight AI.
        
        We store:
        1. Repositories (metadata about what we've analyzed)
        2. Analysis Results (high-level metrics)
        """
        schema_query = """
        CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT,
            local_path TEXT NOT NULL,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_id INTEGER,
            file_count INTEGER,
            total_lines INTEGER,
            summary TEXT,
            FOREIGN KEY (repo_id) REFERENCES repositories (id) ON DELETE CASCADE
        );
        """
        try:
            with self._get_connection() as conn:
                conn.executescript(schema_query)
                logger.info("Database schema initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error initializing schema: {e}")
            raise

    def insert_repository(self, name: str, local_path: str, url: Optional[str] = None) -> int:
        """
        Inserts a new repository record into the database.
        
        Args:
            name (str): The name of the repository.
            local_path (str): The local path where the repository is stored.
            url (Optional[str]): The remote URL if applicable.
            
        Returns:
            int: The ID of the newly inserted repository.
        """
        query = """
        INSERT INTO repositories (name, local_path, url)
        VALUES (?, ?, ?)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name, local_path, url))
            conn.commit()
            return cursor.lastrowid

    def get_repository(self, repo_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a repository record by its ID.
        
        Args:
            repo_id (int): The ID of the repository.
            
        Returns:
            Optional[Dict[str, Any]]: A dictionary representing the repository, or None.
        """
        query = "SELECT * FROM repositories WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (repo_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
