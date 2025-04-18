from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
import requests
import os

app = FastAPI()

# ✅ CORS for Netlify (no trailing slash)
origins = [
    "https://chic-klepon-77ad14.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Jinja2 template setup
env = Environment(loader=FileSystemLoader("templates"))

# ✅ Candidate model
class Candidate(BaseModel):
    Name: str
    College: str
    Degree: str
    Skills: str | List[str]
    Coding_Hours: str
    Projects: str
    LinkedIn: Optional[str] = None
    Portfolio: Optional[str] = None
    Email: Optional[str] = None

# ✅ Request payload model
class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: List[Candidate]

# ✅ Email API route with error logging
@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailRequest):
    try:
        print("✅ Received payload:")
        print(payload.dict())

        # Convert list of skills to comma-separated string if needed
        for candidate in payload.candidates:
            if isinstance(candidate.Skills, list):
                candidate.Skills = ", ".join(candidate.Skills)

        # Render HTML using template
        template = env.get_template("email_template.html")
        html_content = template.render(
            recipient_name=payload.recipient_name,
            candidates=payload.candidates
        )

        # Load Netcore env config
        email_api_url = os.environ.get("EMAIL_API_URL")
        email_api_key = os.environ.get("EMAIL_API_KEY")
        from_email = os.environ.get("FROM_EMAIL")
        from_name = os.environ.get("FROM_NAME")

        if not all([email_api_url, email_api_key, from_email, from_name]):
            raise ValueError("Missing one or more environment variables!")

        # Netcore payload
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
            "api_key": email_api_key
        }

        # Send POST request to Netcore
        response = requests.post(email_api_url, headers=headers, json=netcore_payload)

        print("📨 Netcore Status:", response.status_code)
        print("📨 Netcore Response:", response.text)

        if response.status_code == 200:
            return {"status": "✅ Email sent"}
        else:
            return {"status": "❌ Failed to send", "details": response.text}

    except Exception as e:
        print("❌ Exception in /send_candidate_list_email/:", str(e))
        return {"status": "❌ Error", "message": str(e)}
