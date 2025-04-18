from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
import requests
import os

app = FastAPI()

origins = [
    "https://chic-klepon-77ad14.netlify.app/", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Jinja2 template setup
env = Environment(loader=FileSystemLoader("templates"))

# Candidate model
class Candidate(BaseModel):
    Name: str
    College: str
    Degree: str
    Skills: str | List[str]  # Accept string or list
    Coding_Hours: str
    Projects: str
    LinkedIn: Optional[str] = None
    Portfolio: Optional[str] = None
    Email: Optional[str] = None

# Email payload model
class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: List[Candidate]

@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailRequest):
    print("✅ Received payload:")
    print(payload.dict())

    # 🔧 Convert Skills to comma-separated string if it’s a list
    for candidate in payload.candidates:
        if isinstance(candidate.Skills, list):
            candidate.Skills = ", ".join(candidate.Skills)

    # 🧠 Render HTML email
    template = env.get_template("email_template.html")
    html_content = template.render(
        recipient_name=payload.recipient_name,
        candidates=payload.candidates
    )

    # 🔐 Read .env config
    email_api_url = os.environ.get("EMAIL_API_URL")
    email_api_key = os.environ.get("EMAIL_API_KEY")
    from_email = os.environ.get("FROM_EMAIL")
    from_name = os.environ.get("FROM_NAME")

    # 📬 Build payload for Netcore
    netcore_payload = {
        "from": {
            "email": from_email,
            "name": from_name
        },
        "to": [
            {
                "email": payload.recipient_email,
                "name": payload.recipient_name
            }
        ],
        "subject": payload.subject,
        "htmlContent": html_content
    }

    headers = {
        "Content-Type": "application/json",
        "api-key": email_api_key  # ✅ Fix: was 'api_key'
    }

    # 🚀 Fire the request
    response = requests.post(email_api_url, headers=headers, json=netcore_payload)

    print("📨 Netcore API Status:", response.status_code)
    print("📨 Netcore Response:", response.text)

    if response.status_code == 200:
        return {"status": "Email sent ✅"}
    else:
        return {"status": "❌ Failed to send", "details": response.text}
