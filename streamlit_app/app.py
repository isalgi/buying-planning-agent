import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import uuid
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.session_manager import SessionManager, ContextStore
from rag.embeddings import EmbeddingManager
from rag.vector_store import VectorStore
from rag.retriever import RAGRetriever
from agents.orchestrator import AgentOrchestrator
from config.logging_config import get_logger
from streamlit_app.components import render_sidebar, render_metrics_dashboard
from streamlit_app.styles import apply_custom_styles

logger = get_logger(__name__)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.session_id = None
    st.session_state.orchestrator = None
    st.session_state.chat_history = []

def initialize_system():
    """Initialize the supply planning system"""
    try:
        # Initialize memory components
        session_manager = SessionManager()
        context_store = ContextStore(session_manager)
        
        # Initialize RAG components
        embedding_manager = EmbeddingManager()
        vector_store = VectorStore(embedding_manager)
        retriever = RAGRetriever(vector_store)
        
        # Initialize knowledge base
        retriever.initialize_supply_chain_knowledge()
        
        # Initialize orchestrator
        orchestrator = AgentOrchestrator(context_store, retriever)
        
        # Create session
        session_id = session_manager.create_session(
            user_id="streamlit_user",
            metadata={"source": "streamlit_app"}
        )
        
        st.session_state.initialized = True
        st.session_state.session_id = session_id
        st.session_state.orchestrator = orchestrator
        st.session_context = context_store
        
        logger.info(f"System initialized with session {session_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing system: {str(e)}")
        st.error(f"Failed to initialize system: {str(e)}")
        return False

# Page config
st.set_page_config(
    page_title="Adidas Supply Planning System",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
apply_custom_styles()

# Initialize system if not already initialized
if not st.session_state.initialized:
    with st.spinner("Initializing Adidas Supply Planning System..."):
        if initialize_system():
            st.success("System initialized successfully!")
        else:
            st.stop()

# Main header
st.title("👟 Adidas Supply Planning System")
st.markdown("---")

# Sidebar
with st.sidebar:
    render_sidebar(st.session_state.session_id)

# Main content area
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Demand Forecasting",
    "📏 Size Curve Optimization",
    "💰 Price Optimization",
    "📈 Integrated Planning"
])

with tab1:
    st.header("Demand Forecasting")
    
    col1, col2 = st.columns(2)
    
    with col1:
        product_type = st.selectbox(
            "Product Type",
            ["Footwear", "Apparel", "Accessories", "Equipment"],
            key="demand_product"
        )
        
        region = st.selectbox(
            "Region",
            ["North America", "Europe", "Asia Pacific", "Latin America", "Global"],
            key="demand_region"
        )
        
        forecast_period = st.selectbox(
            "Forecast Period",
            ["Next Quarter", "Next 6 Months", "Next Year", "Next 2 Years"],
            key="demand_period"
        )
    
    with col2:
        st.subheader("Historical Sales Data")
        uploaded_file = st.file_uploader(
            "Upload historical sales (CSV)",
            type=['csv'],
            key="demand_upload"
        )
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
    
    if st.button("Generate Demand Forecast", type="primary", key="demand_btn"):
        with st.spinner("Analyzing data and generating forecast..."):
            # Prepare input data
            input_data = {
                "product_type": product_type.lower(),
                "region": region.lower(),
                "time_period": forecast_period.lower().replace(" ", "_"),
                "historical_data": df.to_dict() if uploaded_file else {},
                "market_trends": ["athletic_trend", "seasonal_patterns"]
            }
            
            # Process request
            result = st.session_state.orchestrator.process_request(
                st.session_state.session_id,
                input_data
            )
            
            if result["success"]:
                st.success("Demand forecast generated successfully!")
                
                # Display results
                forecast_data = result["report"]["detailed_findings"]["demand_forecast"]
                
                # Create visualization
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    y=[1000, 1200, 1500, 1800, 2000, 2200],
                    mode='lines+markers',
                    name='Forecast',
                    line=dict(color='#1f77b4', width=3)
                ))
                fig.add_trace(go.Scatter(
                    x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    y=[900, 1100, 1350, 1620, 1800, 1980],
                    mode='lines',
                    name='Lower Bound (80% CI)',
                    line=dict(color='rgba(31, 119, 180, 0.3)', dash='dash')
                ))
                fig.add_trace(go.Scatter(
                    x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    y=[1100, 1300, 1650, 1980, 2200, 2420],
                    mode='lines',
                    name='Upper Bound (80% CI)',
                    line=dict(color='rgba(31, 119, 180, 0.3)', dash='dash'),
                    fill='tonexty'
                ))
                
                fig.update_layout(
                    title="Demand Forecast with Confidence Intervals",
                    xaxis_title="Month",
                    yaxis_title="Units",
                    hovermode='x unified',
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display forecast text
                st.subheader("Forecast Analysis")
                st.write(forecast_data.get("forecast", "No forecast text available"))
                
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")

with tab2:
    st.header("Size Curve Optimization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        product_category = st.selectbox(
            "Product Category",
            ["Running Shoes", "Training Shoes", "Casual Shoes", "Sandals", "Boots"],
            key="size_product"
        )
        
        target_region = st.selectbox(
            "Target Region",
            ["North America", "Europe", "Asia Pacific", "Middle East", "Global"],
            key="size_region"
        )
        
        use_demand_forecast = st.checkbox("Use latest demand forecast", value=True)
    
    with col2:
        st.subheader("Historical Size Distribution")
        
        # Sample size distribution input
        sizes = ['36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46']
        percentages = st.slider(
            "Adjust size distribution",
            0, 100, (5, 10, 15, 20, 25, 20, 15, 10, 5, 3, 2),
            key="size_dist"
        )
        
        size_data = pd.DataFrame({
            'Size': sizes,
            'Percentage': percentages
        })
        
        fig = px.bar(size_data, x='Size', y='Percentage', 
                     title="Current Size Distribution",
                     color='Percentage',
                     color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    if st.button("Optimize Size Curve", type="primary", key="size_btn"):
        with st.spinner("Optimizing size distribution..."):
            # Get demand forecast if available
            demand_forecast = {}
            if use_demand_forecast and 'last_report' in st.session_state:
                last_report = st.session_state.get('last_report', {})
                demand_forecast = last_report.get('detailed_findings', {}).get('demand_forecast', {})
            
            input_data = {
                "product_category": product_category.lower(),
                "region": target_region.lower(),
                "historical_sizes": size_data.to_dict(),
                "demand_forecast": demand_forecast,
                "special_requirements": ["premium_sizing", "regional_preferences"]
            }
            
            result = st.session_state.orchestrator.process_request(
                st.session_state.session_id,
                input_data
            )
            
            if result["success"]:
                st.success("Size curve optimized successfully!")
                
                # Display optimized curve
                st.subheader("Optimized Size Distribution")
                
                # Sample optimized distribution
                optimized_data = pd.DataFrame({
                    'Size': sizes,
                    'Original': percentages,
                    'Optimized': [p * 1.1 if i < 6 else p * 0.9 for i, p in enumerate(percentages)]
                })
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Original',
                    x=optimized_data['Size'],
                    y=optimized_data['Original'],
                    marker_color='lightgray'
                ))
                fig.add_trace(go.Bar(
                    name='Optimized',
                    x=optimized_data['Size'],
                    y=optimized_data['Optimized'],
                    marker_color='#1f77b4'
                ))
                
                fig.update_layout(
                    title="Size Curve Comparison",
                    xaxis_title="Size",
                    yaxis_title="Percentage (%)",
                    barmode='group',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display recommendations
                st.subheader("Optimization Recommendations")
                size_result = result["report"]["detailed_findings"]["size_curve"]
                st.write(size_result.get("size_curve", "No recommendations available"))
                
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")

with tab3:
    st.header("Price Optimization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        product_name = st.text_input("Product Name", "Ultraboost 22")
        base_cost = st.number_input("Base Cost ($)", min_value=0.0, value=50.0, step=5.0)
        current_price = st.number_input("Current Price ($)", min_value=0.0, value=120.0, step=5.0)
        
        market_segment = st.selectbox(
            "Market Segment",
            ["Premium", "Mid-Range", "Budget", "Performance"],
            key="price_segment"
        )
        
        lifecycle_stage = st.selectbox(
            "Product Lifecycle Stage",
            ["Introduction", "Growth", "Maturity", "Decline"],
            key="lifecycle"
        )
    
    with col2:
        st.subheader("Competitor Pricing")
        
        competitor_data = pd.DataFrame({
            'Competitor': ['Nike', 'Puma', 'Under Armour', 'New Balance'],
            'Price': [125, 110, 115, 105]
        })
        
        fig = px.bar(competitor_data, x='Competitor', y='Price',
                     title="Competitor Price Comparison",
                     color='Price',
                     color_continuous_scale='RdYlGn_r')
        st.plotly_chart(fig, use_container_width=True)
        
        price_elasticity = st.slider(
            "Price Elasticity",
            min_value=0.5,
            max_value=3.0,
            value=1.5,
            step=0.1,
            help="Higher values indicate more price sensitivity"
        )
    
    if st.button("Optimize Price", type="primary", key="price_btn"):
        with st.spinner("Analyzing pricing strategy..."):
            input_data = {
                "product": {
                    "name": product_name,
                    "type": "footwear",
                    "cost": base_cost,
                    "current_price": current_price
                },
                "competitor_prices": competitor_data.to_dict(),
                "market_segment": market_segment.lower(),
                "lifecycle_stage": lifecycle_stage.lower(),
                "costs": {
                    "production": base_cost * 0.6,
                    "marketing": base_cost * 0.2,
                    "distribution": base_cost * 0.2
                },
                "elasticity": price_elasticity
            }
            
            result = st.session_state.orchestrator.process_request(
                st.session_state.session_id,
                input_data
            )
            
            if result["success"]:
                st.success("Price optimization completed!")
                
                # Display price recommendations
                price_result = result["report"]["detailed_findings"]["price_optimization"]
                
                # Create price ladder visualization
                prices = [current_price * 0.9, current_price, current_price * 1.1, current_price * 1.2]
                volumes = [1200, 1000, 800, 600]
                revenues = [p * v for p, v in zip(prices, volumes)]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=prices,
                    y=revenues,
                    mode='lines+markers',
                    name='Revenue Curve',
                    line=dict(color='#2ecc71', width=3),
                    marker=dict(size=10)
                ))
                
                # Mark optimal price
                optimal_idx = revenues.index(max(revenues))
                fig.add_trace(go.Scatter(
                    x=[prices[optimal_idx]],
                    y=[revenues[optimal_idx]],
                    mode='markers',
                    name='Optimal Price',
                    marker=dict(color='red', size=15, symbol='star')
                ))
                
                fig.update_layout(
                    title="Price Optimization Analysis",
                    xaxis_title="Price ($)",
                    yaxis_title="Expected Revenue ($)",
                    hovermode='x'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display pricing strategy
                st.subheader("Recommended Pricing Strategy")
                st.write(price_result.get("pricing_strategy", "No pricing strategy available"))
                
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")

with tab4:
    st.header("Integrated Supply Planning")
    
    # Display current session context
    st.subheader("Current Planning Session")
    st.info(f"Session ID: {st.session_state.session_id}")
    
    # Metrics dashboard
    render_metrics_dashboard()
    
    if st.button("Generate Integrated Plan", type="primary", key="integrated_btn"):
        with st.spinner("Generating comprehensive supply plan..."):
            # Combine inputs from all tabs
            input_data = {
                "product_type": st.session_state.get("demand_product", "footwear"),
                "region": st.session_state.get("demand_region", "global"),
                "forecast_period": st.session_state.get("demand_period", "next_quarter"),
                "product_name": st.session_state.get("product_name", "Ultraboost 22"),
                "product_cost": st.session_state.get("base_cost", 50.0),
                "market_segment": st.session_state.get("price_segment", "premium"),
                "product_lifecycle": st.session_state.get("lifecycle", "maturity")
            }
            
            result = st.session_state.orchestrator.process_request(
                st.session_state.session_id,
                input_data
            )
            
            if result["success"]:
                st.success("Integrated supply plan generated successfully!")
                
                # Store last report in session state
                st.session_state.last_report = result["report"]
                
                # Display executive summary
                st.subheader("📋 Executive Summary")
                st.write(result["report"]["executive_summary"])
                
                # Display recommendations in columns
                st.subheader("🎯 Key Recommendations")
                cols = st.columns(3)
                
                recommendations = result["report"]["recommendations"]
                for i, rec in enumerate(recommendations[:3]):
                    with cols[i]:
                        st.info(f"**Recommendation {i+1}**\n\n{rec}")
                
                # Display integrated plan
                with st.expander("View Detailed Integrated Plan", expanded=False):
                    st.write(result["report"]["integrated_plan"])
                
                # Display risk assessment
                with st.expander("View Risk Assessment", expanded=False):
                    risk_data = result["report"]["risk_assessment"]
                    st.write(risk_data.get("risk_assessment", "No risk assessment available"))
                
                # Display next steps
                st.subheader("📅 Next Steps")
                for step in result["report"]["next_steps"]:
                    st.write(f"• {step}")
                
                # Download button for report
                report_json = json.dumps(result["report"], indent=2)
                st.download_button(
                    label="Download Full Report (JSON)",
                    data=report_json,
                    file_name=f"supply_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
            else:
                st.error(f"Error generating integrated plan: {result.get('error', 'Unknown error')}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Adidas Supply Planning System v1.0 | Powered by LangGraph, OpenAI, and RAG
    </div>
    """,
    unsafe_allow_html=True
)