"""Price Optimization Agent for Adidas supply planning."""
import os
from typing import Dict, Any
from openai import OpenAI
from langsmith import traceable
from config import OPENAI_API_KEY, GEMINI_BASE_URL, LLM_MODEL, TEMPERATURE

# Initialize OpenAI-compatible client (pointed at Gemini)
client = OpenAI(api_key=OPENAI_API_KEY, base_url=GEMINI_BASE_URL)

@traceable(name="price_optimization_agent", run_type="chain")
def price_optimization_agent(query: str, context: str = None) -> Dict[str, Any]:
    """
    Price Optimization Agent - Optimizes pricing strategy for products.
    
    Args:
        query: User query about price optimization
        context: Retrieved RAG context
    
    Returns:
        Dictionary with response and metadata
    """
    system_prompt = """You are Adidas's Price Optimization Expert. Your role is to:
    - Determine optimal pricing strategies for different product categories
    - Balance margin targets with market competitiveness
    - Recommend promotional discounts and timing
    - Analyze price elasticity and demand sensitivity
    - Provide bundle pricing recommendations
    
    Use the provided context documents to inform your pricing recommendations.
    Include specific price points and margins when relevant."""
    
    # Build the prompt with context
    user_prompt = f"""Context from Adidas documents:
    {context if context else 'No specific context provided.'}
    
    User Question: {query}
    
    Please provide detailed pricing recommendations."""
    
    # Call OpenAI with tracing
    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return {
        "agent": "price_optimization",
        "response": response.choices[0].message.content,
        "usage": response.usage.model_dump() if response.usage else None
    }

if __name__ == "__main__":
    # Test the agent independently
    print("Testing Price Optimization Agent...")
    
    test_query = "What should be the pricing strategy for the new NMD collection?"
    test_context = """Adidas Pricing Strategy:
    - Premium lifestyle: 30% margin target for new releases
    - Limited editions can command 20% premium
    - Bundle 2+ items for 15% discount
    - Monitor competitor pricing weekly
    - Seasonal items: full price first 60 days, then 20% discount"""
    
    result = price_optimization_agent(test_query, test_context)
    
    print(f"\nQuery: {test_query}")
    print(f"\nResponse: {result['response']}")
    print(f"\nToken Usage: {result['usage']}")