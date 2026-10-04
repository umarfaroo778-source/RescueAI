# RescueAI

Multi-Agent Emergency Response Decision-Support System — Hackathon MVP.

**Safety:** RescueAI is decision support only. It is not an emergency service, dispatcher, medical system, or replacement for local emergency authorities.

## Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Copy `.env.example` to `.env` for optional live providers.

## Architecture
Streamlit -> Coordinator -> Incident Analyst -> Location & Context -> Environment -> Knowledge/RAG -> Response Planner -> Safety Reviewer.

The offline path works without API keys. External-tool failures are shown rather than invented.
