# Hello Agent Streamlit app

Streamlit frontend for the separate [Hello Agent API](../backend/README.md)
repository. It supports multiple CSV uploads and can also use the example
datasets shipped with the backend.

## Run locally

Start the backend first by following its README, then in this directory run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The app connects to `http://localhost:8000` by default. To use another backend
instance, set `BACKEND_API_URL` in the environment where Streamlit runs; the
backend URL is not exposed as an editable setting in the app.

## Run frontend tests

The UI tests use Streamlit's `AppTest` and mock backend requests, so they do
not require a running backend or model API key. From this directory, run:

```powershell
python -m unittest discover -s tests -v
```
