import redis
import json
import hashlib
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

class SessionManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        self.session_ttl = settings.SESSION_TTL
        
    def create_session(self, user_id: str, metadata: Dict[str, Any] = None) -> str:
        """Create a new session for a user"""
        try:
            session_id = str(uuid.uuid4())
            session_data = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "metadata": metadata or {},
                "context": {}
            }
            
            # Store session data
            self.redis_client.setex(
                f"session:{session_id}",
                self.session_ttl,
                json.dumps(session_data)
            )
            
            logger.info(f"Created session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data"""
        try:
            data = self.redis_client.get(f"session:{session_id}")
            if data:
                session_data = json.loads(data)
                # Update last active
                session_data["last_active"] = datetime.now().isoformat()
                self.redis_client.setex(
                    f"session:{session_id}",
                    self.session_ttl,
                    json.dumps(session_data)
                )
                return session_data
            return None
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {str(e)}")
            return None
    
    def update_session_context(self, session_id: str, context: Dict[str, Any]):
        """Update session context"""
        try:
            session_data = self.get_session(session_id)
            if session_data:
                session_data["context"].update(context)
                self.redis_client.setex(
                    f"session:{session_id}",
                    self.session_ttl,
                    json.dumps(session_data)
                )
        except Exception as e:
            logger.error(f"Error updating session context: {str(e)}")
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        try:
            self.redis_client.delete(f"session:{session_id}")
            logger.info(f"Deleted session {session_id}")
        except Exception as e:
            logger.error(f"Error deleting session: {str(e)}")

class ContextStore:
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    def get_context(self, session_id: str, key: str) -> Optional[Any]:
        """Get specific context value"""
        session = self.session_manager.get_session(session_id)
        if session:
            return session.get("context", {}).get(key)
        return None
    
    def set_context(self, session_id: str, key: str, value: Any):
        """Set specific context value"""
        self.session_manager.update_session_context(session_id, {key: value})
    
    def clear_context(self, session_id: str):
        """Clear all context for a session"""
        session = self.session_manager.get_session(session_id)
        if session:
            session["context"] = {}
            self.session_manager.redis_client.setex(
                f"session:{session_id}",
                self.session_manager.session_ttl,
                json.dumps(session)
            )