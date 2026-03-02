"""Database module for persistent storage with multi-user support."""
import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager
from typing import List, Dict, Optional
import threading
from config import DB_PATH

# Thread-local storage for database connections
_thread_local = threading.local()

class DatabaseManager:
    """Thread-safe database manager for SQLite operations."""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = str(db_path)
        self._init_db()
    
    def _get_connection(self):
        """Get thread-local database connection."""
        if not hasattr(_thread_local, 'connection'):
            _thread_local.connection = sqlite3.connect(
                self.db_path,
                timeout=30,  # Wait up to 30s for lock
                check_same_thread=False  # We're managing threads manually
            )
            _thread_local.connection.row_factory = sqlite3.Row
        return _thread_local.connection
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursors with automatic commit/rollback."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
    
    def _init_db(self):
        """Initialize database tables if they don't exist."""
        with self.get_cursor() as cursor:
            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_query TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,
                    agent_used TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Create index for faster session queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_timestamp 
                ON conversations(session_id, timestamp)
            """)
    
    def save_conversation(self, session_id: str, user_query: str, 
                         assistant_response: str, agent_used: str = None,
                         metadata: Dict = None):
        """Save a conversation turn to database."""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO conversations 
                (session_id, user_query, assistant_response, agent_used, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id, 
                user_query, 
                assistant_response, 
                agent_used,
                json.dumps(metadata) if metadata else None
            ))
    
    def load_session_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Load conversation history for a session."""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT user_query, assistant_response, agent_used, timestamp, metadata
                FROM conversations
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            
            rows = cursor.fetchall()
            return [
                {
                    'user_query': row['user_query'],
                    'assistant_response': row['assistant_response'],
                    'agent_used': row['agent_used'],
                    'timestamp': row['timestamp'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                }
                for row in rows
            ]
    
    def get_all_sessions(self) -> List[str]:
        """Get all unique session IDs."""
        with self.get_cursor() as cursor:
            cursor.execute("SELECT DISTINCT session_id FROM conversations")
            return [row['session_id'] for row in cursor.fetchall()]
    
    def delete_session(self, session_id: str):
        """Delete a session and all its conversations."""
        with self.get_cursor() as cursor:
            cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))


# Global database instance
db_manager = DatabaseManager()

if __name__ == "__main__":
    # Test database functionality
    print("Testing Database Module...")
    
    # Test session
    test_session = "test_session_123"
    
    # Save test conversation
    db_manager.save_conversation(
        session_id=test_session,
        user_query="What is the demand forecast for running shoes?",
        assistant_response="Based on historical data, demand is expected to increase by 15%.",
        agent_used="demand_forecast",
        metadata={"test": True}
    )
    
    # Load history
    history = db_manager.load_session_history(test_session)
    print(f"✓ Saved and loaded {len(history)} conversations")
    
    # List all sessions
    sessions = db_manager.get_all_sessions()
    print(f"✓ Active sessions: {sessions}")
    
    # Cleanup
    db_manager.delete_session(test_session)
    print("✓ Test session cleaned up")