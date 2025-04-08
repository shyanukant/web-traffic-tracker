# web-traffic-tracker

### Run Commands

Backend : 
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Frontend :
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Static site :
```bash
python -m http.server 8080
```