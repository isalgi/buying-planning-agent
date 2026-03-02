✅ To Run the System:
Install dependencies:

bash
pip install -r requirements.txt
Set OpenAI API key:

bash
export OPENAI_API_KEY="your-key-here"
Run tests for each module:

bash
python db.py
python rag.py
python agents/demand_agent.py
python agents/size_curve_agent.py
python agents/price_agent.py
python router.py
python graph.py
Start the Streamlit app:

bash
streamlit run app.py
Use CLI interface:

bash
python main.py --interactive
python main.py --query "forecast demand for running shoes"
The system is fully functional, scalable, and ready for demonstration in an interview setting. Each component is modular and can be extended with more sophisticated logic while maintaining the same architecture.