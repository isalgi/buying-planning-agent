import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

def render_sidebar(session_id):
    """Render sidebar components"""
    st.image("https://1000logos.net/wp-content/uploads/2022/06/Adidas-Logo-1971.png", width=200)
    
    st.header("Supply Planning System")
    
    # Session info
    st.subheader("Session Information")
    st.info(f"Session ID: {session_id[:8]}...")
    st.caption(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Quick actions
    st.subheader("Quick Actions")
    if st.button("🔄 New Session"):
        st.session_state.initialized = False
        st.rerun()
    
    if st.button("📊 Load Sample Data"):
        st.session_state.load_sample = True
        st.success("Sample data loaded!")
    
    # System status
    st.subheader("System Status")
    status_cols = st.columns(2)
    with status_cols[0]:
        st.metric("Agents", "3/3 Active", delta=None)
    with status_cols[1]:
        st.metric("RAG Status", "Connected", delta=None)
    
    # Recent activities
    st.subheader("Recent Activities")
    activities = [
        "Demand forecast generated",
        "Size curve optimized",
        "Price analysis completed"
    ]
    for activity in activities[:3]:
        st.caption(f"• {activity}")
    
    # Help section
    with st.expander("Need Help?"):
        st.markdown("""
        **How to use:**
        1. Navigate through tabs
        2. Input product details
        3. Run individual analyses
        4. Generate integrated plan
        
        **Contact Support:**
        supply.planning@adidas.com
        """)

def render_metrics_dashboard():
    """Render metrics dashboard"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Forecast Accuracy",
            value="87%",
            delta="2%",
            help="Last 30 days average"
        )
    
    with col2:
        st.metric(
            label="Inventory Turnover",
            value="5.2x",
            delta="0.3x",
            help="Annualized rate"
        )
    
    with col3:
        st.metric(
            label="Fill Rate",
            value="94%",
            delta="-1%",
            help="Order fulfillment rate"
        )
    
    with col4:
        st.metric(
            label="Gross Margin",
            value="42%",
            delta="1.5%",
            help="Average across products"
        )
    
    # Performance chart
    st.subheader("Performance Trends")
    
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    metrics_df = pd.DataFrame({
        'Date': dates,
        'Forecast Accuracy': [85 + i*0.2 for i in range(30)],
        'Fill Rate': [92 + i*0.1 for i in range(30)],
        'Inventory Turnover': [4.5 + i*0.05 for i in range(30)]
    })
    
    fig = go.Figure()
    for metric in ['Forecast Accuracy', 'Fill Rate', 'Inventory Turnover']:
        fig.add_trace(go.Scatter(
            x=metrics_df['Date'],
            y=metrics_df[metric],
            mode='lines',
            name=metric,
            line=dict(width=2)
        ))
    
    fig.update_layout(
        title="Key Metrics Trend (Last 30 Days)",
        xaxis_title="Date",
        yaxis_title="Value",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)