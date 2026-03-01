import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles"""
    st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Header styling */
    .stTitle {
        color: #1f77b4;
        font-weight: bold;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #135e8f;
        color: white;
        border: none;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Metric card styling */
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Success message styling */
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
    }
    
    /* Error message styling */
    .stError {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
    }
    
    /* Info message styling */
    .stInfo {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 5px;
        font-weight: bold;
    }
    
    /* Dataframe styling */
    .dataframe {
        border: 1px solid #dee2e6;
        border-radius: 5px;
        overflow: hidden;
    }
    
    /* Plotly chart container */
    .js-plotly-plot {
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        padding: 1rem;
        background-color: white;
    }
    
    /* Card styling for sections */
    .css-1r6slb0 {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Footer styling */
    footer {
        visibility: hidden;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #1f77b4;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #135e8f;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main {
            padding: 0rem 0.5rem;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            flex-wrap: wrap;
        }
    
        @media (max-width: 768px) {
        .stTabs [data-baseweb="tab"] {
            font-size: 0.9rem;
            padding: 0.3rem 0.6rem;
        }
    }
    
    /* Loading spinner */
    .stSpinner {
        text-align: center;
        color: #1f77b4;
    }
    
    /* Divider styling */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #e9ecef;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border-radius: 5px;
        border: 1px solid #ced4da;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1f77b4;
        box-shadow: 0 0 0 0.2rem rgba(31, 119, 180, 0.25);
    }
    
    /* Select box styling */
    .stSelectbox > div > div > select {
        border-radius: 5px;
        border: 1px solid #ced4da;
    }
    
    /* Number input styling */
    .stNumberInput > div > div > input {
        border-radius: 5px;
        border: 1px solid #ced4da;
    }
    
    /* File uploader styling */
    .stFileUploader {
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    
    /* Checkbox styling */
    .stCheckbox {
        font-weight: normal;
    }
    
    /* Radio button styling */
    .stRadio > div {
        gap: 1rem;
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background-color: #1f77b4;
    }
    
    /* Tooltip styling */
    .stTooltip {
        background-color: #333;
        color: white;
        border-radius: 3px;
        padding: 0.25rem 0.5rem;
        font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)