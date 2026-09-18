# AIVOA - AI-Powered Customer Complaint Management System

This project is an AI-powered QMS module for the pharmaceutical industry, utilizing a modern tech stack.

## Tech Stack
- **Frontend**: React, Vite, Tailwind CSS v4, Redux Toolkit, Google Inter Font.
- **Backend**: Python, FastAPI, SQLAlchemy (SQLite configured by default, easily swappable to PostgreSQL).
- **AI Agent Framework**: LangGraph, LangChain, Groq API (gemma2-9b-it / llama-3.3-70b-versatile).

## Prerequisites
1. **Python 3.10+**: Must be installed on your system.
2. **Node.js 18+**: Must be installed.
3. **Groq API Key**: You need an API key from [Groq Console](https://console.groq.com/keys).

## Step 1: Backend Setup
1. Open a terminal and navigate to the `backend` folder.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pydantic langgraph langchain-groq langchain-core
   ```
5. Configure API Key:
   - Open `backend/.env` and replace `your_groq_api_key_here` with your actual Groq API key.
6. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```
   The backend will run on `http://localhost:8000`.

## Step 2: Frontend Setup
1. Open a **new** terminal and navigate to the `frontend` folder.
2. Install dependencies (already initialized, but good to ensure):
   ```bash
   npm install
   ```
3. Run the frontend development server:
   ```bash
   npm run dev
   ```
4. Open the displayed URL (usually `http://localhost:5173`) in your browser.

## Step 3: Recording the Demo Video
1. Open the UI.
2. Paste a mock pharmaceutical complaint in the AI Assistant text area (e.g., "Email from John Doe: We received batch B12345 of Paracetamol 500mg today. Around 100kg of the tablets were crushed and broken. Please investigate. Severity is critical.").
3. Click "Extract Details".
4. Show how the AI (via LangGraph) extracts the info and automatically populates the form on the left.
5. Show the AI Copilot Risk Assessment (Bonus feature) that provides Risk Class, Root Cause Hypothesis, and CAPA.
6. Click "Save Complaint" to save it to the database.
