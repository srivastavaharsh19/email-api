from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader, select_autoescape
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: list

# Setup Jinja2 environment
env = Environment(
    loader=FileSystemLoader("templates"),  # ✅ use correct folder
    autoescape=select_autoescape()
)

# Load email template
template = env.get_template("email_template.html")

@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailRequest):
    print("✅ Received payload:", payload.dict())

    # Render HTML content from template
    html_content = template.render(
        recipient_name=payload.recipient_name,
        subject=payload.subject,
        candidates=payload.candidates
    )

    # ✅ Hardcoded From Info
    from_email = "pst@emails.testbook.com"
    from_name = "PST Team"

    # Build payload for Netcore
    data = {
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

    # ✅ DEBUG: Print env vars
    api_key = os.getenv("EMAIL_API_KEY")
    api_url = os.getenv("EMAIL_API_URL")

    print("🔑 Debug: Loaded API Key =", api_key if api_key else "❌ NOT FOUND")
    print("🔗 Debug: Loaded API URL =", api_url if api_url else "❌ NOT FOUND")

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key
    }

    session = requests.Session()
    req = requests.Request("POST", api_url, headers=headers, json=data)
    prepped = session.prepare_request(req)

    print("📬 From Email:", from_email)
    print("📬 From Name:", from_name)
    print("📦 Final Netcore Payload:", data)
    print("🚀 Prepared Headers Sent:", prepped.headers)

    # Send the request
    response = session.send(prepped)

    print("📨 Netcore Status:", response.status_code)
    print("📨 Netcore Response:", response.text)

    return {
        "status": "✅ Email API response" if response.status_code == 202 else "❌ Failed to send",
        "details": response.text
    }
