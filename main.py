"""
Simple standalone runner for Adidas Supply Planning System.
Run the graph directly without Streamlit UI.
"""
import uuid
from graph import supply_planning_graph
from db import db_manager

# Store conversation history per session
sessions = {}

def run_query(query, session_id=None, history=None):
    """Run a single query and print the result."""
    
    # Use provided session_id or create new one
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    # Initialize session history if not exists
    if session_id not in sessions:
        sessions[session_id] = []
    
    # Use provided history or get from sessions
    if history is None:
        history = sessions[session_id]
    
    print(f"\n{'='*50}")
    print(f"Session: {session_id[:8]}...")
    print(f"Query: {query}")
    print(f"{'='*50}")
    
    # Convert history to conversation context string
    conversation_context = ""
    if history:
        context_parts = []
        for msg in history:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                role = "User" if msg["role"] == "user" else "Assistant"
                context_parts.append(f"{role}: {msg['content']}")
            elif isinstance(msg, (list, tuple)) and len(msg) == 2:
                user_msg, assistant_msg = msg
                context_parts.append(f"User: {user_msg}")
                context_parts.append(f"Assistant: {assistant_msg}")
        
        # Use last 6 messages (3 exchanges) for context
        conversation_context = "\n".join(context_parts[-6:])
    
    # Initialize state with conversation context
    state = {
        "query": query,
        "session_id": session_id,
        "conversation_context": conversation_context,
        "intent": "",
        "intent_confidence": 0.0,
        "intent_reasoning": "",
        "rag_context": "",
        "agent_response": "",
        "agent_used": "",
        "usage": {},
        "error": ""
    }
    
    # Run the graph
    try:
        result = supply_planning_graph.invoke(state)
        
        if result.get("error"):
            print(f"Error: {result['error']}")
            # Store error in history
            sessions[session_id].append({
                "role": "user", 
                "content": query
            })
            sessions[session_id].append({
                "role": "assistant", 
                "content": f"Error: {result['error']}"
            })
        else:
            print(f"\nAgent: {result['agent_used']}")
            print(f"Intent: {result['intent']} ({result['intent_confidence']:.2f})")
            print(f"\nResponse: {result['agent_response']}")
            
            if result.get("usage"):
                tokens = result['usage'].get('total_tokens', 0)
                print(f"\nTokens: {tokens}")
            
            # Store successful response in history
            sessions[session_id].append({
                "role": "user", 
                "content": query
            })
            sessions[session_id].append({
                "role": "assistant", 
                "content": result['agent_response']
            })
        
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        # Store error in history
        sessions[session_id].append({
            "role": "user", 
            "content": query
        })
        sessions[session_id].append({
            "role": "assistant", 
            "content": f"Error: {str(e)}"
        })
        return None

def display_history(history):
    """Display conversation history in a readable format."""
    if not history:
        print("No conversation history yet.")
        return
    
    print("\n" + "="*60)
    print("CONVERSATION HISTORY")
    print("="*60)
    
    for i, msg in enumerate(history):
        if msg["role"] == "user":
            print(f"\n👤 You: {msg['content']}")
        else:
            print(f"🤖 AI: {msg['content']}")
            if i < len(history) - 1:
                print("-" * 40)

def interactive():
    """Simple interactive mode."""
    session_id = str(uuid.uuid4())
    print("\n" + "="*60)
    print("Adidas Supply Planning System")
    print("="*60)
    print("Commands:")
    print("  'quit' - Exit the program")
    print("  'history' - Show full conversation history")
    print("  'clear' - Clear current session history")
    print("  'new' - Start a new session")
    print("="*60)
    
    while True:
        query = input("\nYou: ").strip()
        
        if query.lower() == 'quit':
            print("Goodbye!")
            break
            
        elif query.lower() == 'history':
            display_history(sessions.get(session_id, []))
            
        elif query.lower() == 'clear':
            sessions[session_id] = []
            print("✓ Conversation history cleared")
            
        elif query.lower() == 'new':
            session_id = str(uuid.uuid4())
            sessions[session_id] = []
            print(f"✓ New session started (ID: {session_id[:8]}...)")
            
        elif query:
            run_query(query, session_id)

def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1:
        # Run single query from command line
        query = ' '.join(sys.argv[1:])
        run_query(query)
    else:
        # Run interactive mode
        interactive()

if __name__ == "__main__":
    main()