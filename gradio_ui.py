"""
Adidas Supply Planning System - UI
Run with: python gradio_ui.py
"""
import uuid
import gradio as gr
from graph import supply_planning_graph
from db import db_manager

# Store session per user
sessions = {}

def process_query(query, history, session_id):
    """Process a single query and return response."""
    
    # Create or get session
    if not session_id:
        session_id = str(uuid.uuid4())
        sessions[session_id] = []
    
    # Convert Gradio history to conversation context string
    conversation_context = ""
    if history:
        context_parts = []
        for msg in history:
            # Handle MessageDict format (role, content)
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                role = "User" if msg["role"] == "user" else "Assistant"
                context_parts.append(f"{role}: {msg['content']}")
        
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
    
    try:
        # Run graph with full context
        result = supply_planning_graph.invoke(state)
        
        if result.get("error"):
            response = f"❌ Error: {result['error']}"
        else:
            # Format response
            agent = result['agent_used']
            intent = result['intent']
            confidence = result['intent_confidence']
            answer = result['agent_response']
            
            response = f"""**Agent:** {agent}  
**Intent:** {intent} ({confidence:.2f})  

{answer}"""
            
            if result.get("usage"):
                tokens = result['usage'].get('total_tokens', 0)
                response += f"\n\n---\n*Tokens: {tokens}*"
        
        # Update history with MessageDict format for Gradio 6.8.0
        if history is None:
            history = []
        
        # Use MessageDict format with role and content
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": response})
        
        # Store in sessions dict
        if session_id in sessions:
            sessions[session_id] = history
        
        return "", history, session_id
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        if history is None:
            history = []
        
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": error_msg})
        
        if session_id in sessions:
            sessions[session_id] = history
            
        return "", history, session_id

def clear_chat(session_id):
    """Clear chat history for a session."""
    if session_id in sessions:
        sessions[session_id] = []
    return [], session_id

def view_history(session_id):
    """View full session history from DB."""
    if not session_id:
        return "No active session"
    
    history = db_manager.load_session_history(session_id)
    if not history:
        return "No history found"
    
    output = f"## Session History: {session_id}\n\n"
    for msg in history:
        output += f"**You:** {msg['user_query']}\n\n"
        output += f"**AI ({msg['agent_used']}):** {msg['assistant_response']}\n\n"
        output += "---\n\n"
    
    return output

def create_session():
    """Create a new session and return session ID."""
    session_id = str(uuid.uuid4())
    sessions[session_id] = []
    return session_id

# Create Gradio interface
with gr.Blocks(title="Adidas Supply Planning", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 👟 Adidas Supply Planning System
    Ask about demand forecasting, size curves, or pricing optimization.
    """)
    
    # Store session state - initialize with new session
    session_state = gr.State(create_session)
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="Conversation",
                height=500,
                type="messages"
            )
            msg = gr.Textbox(label="Your Question", placeholder="e.g., What is demand forecast for Ultraboost?")
            
            with gr.Row():
                submit = gr.Button("Send", variant="primary")
                clear = gr.Button("Clear Chat")
        
        with gr.Column(scale=1):
            gr.Markdown("### Session Info")
            session_id_display = gr.Textbox(
                label="Session ID", 
                value="",  # Will be updated
                interactive=False
            )
            
            new_session_btn = gr.Button("🆕 New Session", variant="secondary")
            
            gr.Markdown("### Sample Queries")
            sample_queries = gr.Dataset(
                components=[msg],
                samples=[
                    ["What is the demand forecast for Ultraboost in Q4?"],
                    ["Optimize size curve for running shoes in Asia"],
                    ["What about for running shoes in Europe?"],
                    ["What price should I set for the new NMD collection?"],
                    ["Tell me about Adidas supply chain operations"]
                ],
                label="Click to try"
            )
            
            history_btn = gr.Button("View Full History")
            history_output = gr.Markdown()
    
    # Event handlers
    def respond(message, chat_history, session_id):
        if not message:
            return "", chat_history, session_id
        
        # Ensure chat_history is a list
        if chat_history is None:
            chat_history = []
        
        return process_query(message, chat_history, session_id)
    
    def update_session_id(session_id):
        return session_id if session_id else "No active session"
    
    def new_session():
        """Create new session and clear chat."""
        new_id = str(uuid.uuid4())
        sessions[new_id] = []
        return [], new_id, new_id
    
    def clear_chat_handler(session_id):
        """Clear chat history handler."""
        if session_id in sessions:
            sessions[session_id] = []
        return [], session_id
    
    # Connect events
    submit.click(respond, [msg, chatbot, session_state], [msg, chatbot, session_state])
    msg.submit(respond, [msg, chatbot, session_state], [msg, chatbot, session_state])
    
    sample_queries.click(lambda x: x[0], [sample_queries], [msg])
    
    clear.click(clear_chat_handler, [session_state], [chatbot, msg])
    
    new_session_btn.click(new_session, None, [chatbot, session_state, session_id_display])
    
    session_state.change(update_session_id, [session_state], [session_id_display])
    
    history_btn.click(view_history, [session_state], [history_output])
    
    # Initialize session ID display on load
    demo.load(lambda s: s, [session_state], [session_id_display])

if __name__ == "__main__":
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7860
    )