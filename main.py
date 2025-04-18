from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
import requests
import os

app = FastAPI()

# CORS setup
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

# Jinja2 email template setup
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

@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailRequest):
    print("✅ Received payload:")
    print(payload.dict())

    # Convert skills to comma-separated if needed
    for candidate in payload.candidates:
        if isinstance(candidate.Skills, list):
            candidate.Skills = ", ".join(candidate.Skills)

    # Render email HTML
    template = env.get_template("email_template.html")
    html_content = template.render(
        recipient_name=payload.recipient_name,
        candidates=payload.candidates
    )

    # ✅ Hardcoded working values
    from_email = "pst@emails.testbook.com"
    from_name = "PST Team"
    email_api_url = "https://emailapi.netcorecloud.net/v5.1/mail/send"
    email_api_key = "12f88c25be606f95bf4cfee3d3f58746"

    print("📬 From Email:", from_email)
    print("📬 From Name:", from_name)

    netcore_payload = {
        "from": {
            "email": str(from_email),
            "name": str(from_name)
        },
        "personalizations": [
            {
                "to": [
                    {
                        "email": payload.recipient_email,
                        "name": payload.recipient_name
                    }
                ],
                "subject": payload.subject
            }
        ],
        "content": [
            {
                "type": "html",   # ✅ REQUIRED by Netcore
                "value": html_content
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "api_key": email_api_key
    }

    response = requests.post(email_api_url, headers=headers, json=netcore_payload)

    print("📨 Netcore Status:", response.status_code)
    print("📨 Netcore Response:", response.text)

    if response.status_code == 200:
        return {"status": "✅ Email sent"}
    else:
        return {
            "status": "❌ Failed to send",
            "details": response.text
        }
