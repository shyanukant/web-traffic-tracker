from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# Enable CORS for all domains (for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store tracking data in memory for now
VISITS = []

@app.post("/track")
async def track(request: Request):
    data = await request.json()
    visitor = {
        "ip": request.client.host,
        "user_agent": data.get("userAgent"),
        "referrer": data.get("referrer"),
        "page": data.get("page"),
        "screen": f"{data.get('screenWidth')}x{data.get('screenHeight')}",
        "timestamp": data.get("timestamp", datetime.utcnow().isoformat())
    }
    VISITS.append(visitor)
    return {"status": "ok"}

@app.get("/data")
def get_data():
    return VISITS
