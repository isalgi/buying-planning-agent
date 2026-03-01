Local Development

# Clone the repository
git clone <repository-url>
cd adidas_supply_planning

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key

# Run the application
python main.py --mode streamlit


Docker Deployment

# Build and run with Docker Compose
docker-compose up --build

# Access the application
# Streamlit UI: http://localhost:8501
# API: http://localhost:8000