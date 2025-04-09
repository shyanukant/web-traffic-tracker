from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from user_agents import parse as ua_parse
import requests
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Visit, Website

engine = create_engine("sqlite:///./tracker.db")
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_geo_data(ip):
    try:
        if ip.startswith("127.") or ip.startswith("::1"):
            return {"city": "Localhost", "region": "", "country": "Local"}
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        return response.json()
    except:
        return {}

@app.post("/register")
async def register_site(data: dict):
    db = SessionLocal()
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
    return {"status": "registered", "message": "Website registered successfully"}  # ✅ Added message


@app.post("/track")
async def track(request: Request):
    data = await request.json()
    # print("📥 Incoming tracking data:", data)  # ✅ Debug

    db = SessionLocal()
    domain = data.get("site")
    # print("🌐 Tracking domain:", domain)
    # print("🧠 Registered domains:", [w.domain for w in db.query(Website).all()])
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


@app.get("/websites")
async def get_websites():
    db = SessionLocal()
    websites = db.query(Website).all()
    db.close()
    return [{"domain": w.domain, "name": w.name} for w in websites]

@app.get("/debug/visits")
def debug_visits():
    db = SessionLocal()
    visits = db.query(Visit).all()
    db.close()
    return [v.__dict__ for v in visits]
