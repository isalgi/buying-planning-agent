"""
Unit tests for agents
"""

import pytest
from unittest.mock import Mock, patch
from agents.demand_forecast_agent import DemandForecastAgent
from agents.size_curve_agent import SizeCurveAgent
from agents.price_optimization_agent import PriceOptimizationAgent

@pytest.fixture
def mock_context_store():
    return Mock()

@pytest.fixture
def mock_retriever():
    return Mock()

def test_demand_forecast_agent_initialization(mock_context_store, mock_retriever):
    agent = DemandForecastAgent(mock_context_store, mock_retriever)
    assert agent.name == "DemandForecast"
    assert agent.context_store == mock_context_store
    assert agent.retriever == mock_retriever

def test_demand_forecast_agent_process(mock_context_store, mock_retriever):
    agent = DemandForecastAgent(mock_context_store, mock_retriever)
    
    # Mock the graph invoke
    agent.graph.invoke = Mock(return_value={
        "forecast": "Test forecast",
        "analysis": {"test": "data"},
        "validation": {"status": "accepted"}
    })
    
    result = agent.process("test_session", {"product_type": "footwear"})
    
    assert "forecast" in result
    assert "analysis" in result
    assert "validation" in result

# Add more tests as needed