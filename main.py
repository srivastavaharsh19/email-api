from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://zp1v56uxy8rdx5ypatb0ockcb9tr6a-oci3-upn8vii4--5173--fb22cd3d.local-credentialless.webcontainer-api.io"
    ],
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
    Skills: str | List[str]  # Support both string and array
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

    # Fix: Convert skills list to comma-separated string if needed
    for candidate in payload.candidates:
        if isinstance(candidate.Skills, list):
            candidate.Skills = ", ".join(candidate.Skills)

    # Load and render email template
    template = env.get_template("email_template.html")
    html_content = template.render(
        recipient_name=payload.recipient_name,
        candidates=payload.candidates
    )

    # Load env variables
    email_api_url = os.environ.get("EMAIL_API_URL")
    email_api_key = os.environ.get("EMAIL_API_KEY")
    from_email = os.environ.get("FROM_EMAIL")
    from_name = os.environ.get("FROM_NAME")

    # Construct Netcore payload
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

    # Send to Netcore
    response = requests.post(email_api_url, headers=headers, json=netcore_payload)

    print("📨 Netcore API Status:", response.status_code)
    print("📨 Netcore Response:", response.text)

    if response.status_code == 200:
        return {"status": "Email sent ✅"}
    else:
        return {"status": "❌ Failed to send", "details": response.text}
