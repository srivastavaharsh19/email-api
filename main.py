from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
import requests
import os

app = FastAPI()

# CORS
origins = ["https://chic-klepon-77ad14.netlify.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Template setup
env = Environment(loader=FileSystemLoader("templates"))

# Models
class Candidate(BaseModel):
    Name: str
    College: str
    Degree: str
    Skills: str | List[str]
    Coding_Hours: str
    Projects: str
    LinkedIn: Optional[str] = ""
    Portfolio: Optional[str] = ""
    Email: Optional[str] = ""

class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: List[Candidate]

# Email endpoint
@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailRequest):
    print("✅ Received payload:")
    print(payload.dict())

    # Convert Skills from list to comma-separated string
    for c in payload.candidates:
        if isinstance(c.Skills, list):
            c.Skills = ", ".join(c.Skills)

    # Render template
    template = env.get_template("email_template.html")
    html_content = template.render(
        recipient_name=payload.recipient_name,
        candidates=payload.candidates
    )

    # Hardcoded sender
    from_email = str("connect@emails.testbook.com").strip().replace('"', '').replace("'", "")
    from_name = str("Polaris Campus").strip().replace('"', '').replace("'", "")

    # Netcore payload
    netcore_payload = {
        "personalizations": [
            {
                "to": [{"email": payload.recipient_email, "name": payload.recipient_name}],
                "subject": payload.subject,
            }
        ],
        "from": {
            "email": from_email,
            "name": from_name
        },
        "content": [
            {
                "type": "html",
                "value": html_content
            }
        ]
    }

    print("📬 From Email:", from_email)
    print("📬 From Name:", from_name)
    print("📦 Final Netcore Payload:")
    print(netcore_payload)

    # Headers
    headers = {
        "Content-Type": "application/json",
        "api_key": os.getenv("EMAIL_API_KEY")
    }

    email_api_url = os.getenv("EMAIL_API_URL")
    response = requests.post(email_api_url, headers=headers, json=netcore_payload)

    print("📨 Netcore Status:", response.status_code)
    print("📨 Netcore Response:", response.text)

    if response.status_code == 200:
        return {"status": "✅ Email sent successfully!"}
    else:
        return {
            "status": "❌ Failed to send",
            "details": response.text
        }
