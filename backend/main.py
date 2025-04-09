from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from user_agents import parse as ua_parse
import requests
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from models import Base, Visit, Website

engine = create_engine("sqlite:///./tracker.db")
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


app = FastAPI()

# Middleware to handle CORS()
class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        method = request.method
        # print("🧾 Request origin:", origin)
        allowed_origin = False
        if origin:
            db = SessionLocal()
            domains = [w.domain.rstrip("/") for w in db.query(Website).all()]
            db.close()
            origin_hostname = origin.replace("http://", "").replace("https://", "").split(":")[0]
            if origin.rstrip("/") in domains or origin_hostname in domains:
                allowed_origin = True
        # Allow Options method for preflight requests
        if method == "OPTIONS":
            response = Response(status_code=204)
        else:
            response: Response = await call_next(request)

        if allowed_origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            response.headers["Access-Control-Allow-Credentials"] = "true"

        return response
    
# Add the CORS middleware to the app
app.add_middleware(CustomCORSMiddleware)

# Uncomment the following lines if you want to allow all origins
'''
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
'''

def get_geo_data(ip):
    try:
        if ip.startswith("127.") or ip.startswith("::1"):
            return {"city": "Localhost", "region": "", "country": "Local"}
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        return response.json()
    except:
        return {}

# Register websites 
@app.post("/register")
async def register_site(data: dict):
    db = SessionLocal()
    # domain = data.get("domain")
    raw_domain = data.get("domain")
    parsed = requests.utils.urlparse(raw_domain)
    domain = parsed.hostname or raw_domain # # extracts "127.0.0.1" from "http://127.0.0.1"
    name = data.get("name")

    existing = db.query(Website).filter_by(domain=domain).first()
    if existing:
        db.close()
        return {"status": "exists", "message": "Website already registered"}

    website = Website(domain=domain, name=name)
    db.add(website)
    db.commit()
    db.close()

    script = f'<script async src="{API_BASE_URL}/tracker.js" data-site="{domain}"></script>'
    return {"status": "registered", "script": script, "message": "Website registered successfully"}  # ✅ Added message

@app.get("/tracker.js", response_class=HTMLResponse)
def serve_tracker_script():
    js_code = """
    (function () {
        const data = {
            userAgent: navigator.userAgent,
            screen: `${screen.width}x${screen.height}`,
            url: location.href,
            referrer: document.referrer,
            time: new Date().toISOString(),
            site: document.currentScript.getAttribute("data-site").replace(/\/$/, "")
        };

        fetch("http://127.0.0.1:8000/track", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        }).then(res => res.json()).then(console.log).catch(console.error);
    })();
    """
    return HTMLResponse(content=js_code, media_type="application/javascript")

@app.post("/track")
async def track(request: Request):
    data = await request.json()
    # print("📥 Incoming tracking data:", data)  # ✅ Debug
    origin = request.headers.get("origin")
    
    print("🧾 Request origin:", origin)
    db = SessionLocal()
    domain = data.get("site").rstrip("/")  # Remove trailing slash if present
    print("🌐 Tracking domain:", domain)
    print("🧠 Registered domains:", [w.domain for w in db.query(Website).all()])
    website = db.query(Website).filter_by(domain=domain).first()

    print("🔍 Website matched:", website)  # ✅ Debug

    if not website:
        db.close()
        return {"error": "Unregistered site"}

    ip = request.client.host
    print("🌐 IP Address:", ip)  # ✅ Debug

    user_agent_str = data.get("userAgent", "")
    print("🧠 User Agent:", user_agent_str)  # ✅ Debug

    ua = ua_parse(user_agent_str)
    geo = get_geo_data(ip)
    print("📍 Geo data:", geo)  # ✅ Debug

    visit = Visit(
        website_id=website.id,
        ip=ip,
        city=geo.get("city"),
        region=geo.get("region"),
        country=geo.get("country"),
        location=geo.get("loc"),
        org=geo.get("org"),
        browser=ua.browser.family,
        browser_version=ua.browser.version_string,
        os=ua.os.family,
        device=ua.device.family,
        url=data.get("url"),
        referrer=data.get("referrer"),
        screen=data.get("screen")
    )
    db.add(visit)
    db.commit()
    db.close()
    print("✅ Visit saved!")
    return {"status": "tracked"}


@app.get("/websites")
async def get_websites():
    db = SessionLocal()
    websites = db.query(Website).all()
    db.close()
    domains = [w.domain.rstrip("/") for w in db.query(Website).all()]
    print("🌐 Registered domains:", domains)
    return [{"domain": w.domain, "name": w.name} for w in websites]

@app.get("/data/{name}")
async def get_data(name: str):
    db = SessionLocal()
    website = db.query(Website).filter_by(name=name).first()
    if not website:
        db.close()
        return []

    visits = db.query(Visit).filter_by(website_id=website.id).all()
    db.close()
    return [v.__dict__ for v in visits]

@app.get("/debug/visits")
def debug_visits():
    db = SessionLocal()
    visits = db.query(Visit).all()
    db.close()
    return [v.__dict__ for v in visits]
