"""Size Curve Optimization Agent for Adidas supply planning."""
import os
from typing import Dict, Any
from openai import OpenAI
from langsmith import traceable
from config import OPENAI_API_KEY, LLM_MODEL, TEMPERATURE

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

@traceable(name="size_curve_agent", run_type="chain")
def size_curve_agent(query: str, context: str = None) -> Dict[str, Any]:
    """
    Size Curve Optimization Agent - Optimizes size distribution for products.
    
    Args:
        query: User query about size curve optimization
        context: Retrieved RAG context
    
    Returns:
        Dictionary with response and metadata
    """
    system_prompt = """You are Adidas's Size Curve Optimization Specialist. Your role is to:
    - Analyze optimal size distributions for different product categories
    - Account for regional and demographic variations
    - Recommend size curves based on historical sales data
    - Minimize stockouts and overstock across sizes
    - Adjust curves for specific product types (running, lifestyle, training)
    
    Use the provided context documents to inform your recommendations.
    Provide specific percentages for size distributions."""
    
    # Build the prompt with context
    user_prompt = f"""Context from Adidas documents:
    {context if context else 'No specific context provided.'}
    
    User Question: {query}
    
    Please provide detailed size curve recommendations."""
    
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
        "agent": "size_curve",
        "response": response.choices[0].message.content,
        "usage": response.usage.model_dump() if response.usage else None
    }

if __name__ == "__main__":
    # Test the agent independently
    print("Testing Size Curve Optimization Agent...")
    
    test_query = "What size curve should I use for Superstar shoes in the Asian market?"
    test_context = """Adidas Size Curve Best Practices:
    - Lifestyle shoes like Superstar have broader size distribution
    - Asian markets need sizes 1.5 smaller on average
    - Popular sizes 7-9 represent 70% of sales in Asia
    - Unisex styles need adjusted curves for gender differences"""
    
    result = size_curve_agent(test_query, test_context)
    
    print(f"\nQuery: {test_query}")
    print(f"\nResponse: {result['response']}")
    print(f"\nToken Usage: {result['usage']}")