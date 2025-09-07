# Marketplace Agents (FastAPI)

An AI-powered FastAPI backend that provides:
- Price Suggestion Agent
- Moderation Agent

## Setup

1. Clone repo:
   ```bash
   git clone https://github.com/your-username/marketplace-agents-fastapi.git
   cd marketplace-agents-fastapi

2. Create virtual environment (optional but recommended):

python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

3. Install dependencies:

pip install -r requirements.txt

4. Create a .env file:

GROQ_API_KEY=your_api_key_here

5. Run server:
uvicorn main:app --reload
