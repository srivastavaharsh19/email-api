from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader, select_autoescape
import requests
import os

app = FastAPI()

# Allow CORS for local/Netlify testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Payload model
class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: list

# ✅ Fix the template path to look inside /templates
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape()
)

# ✅ Load the correct file name
template = env.get_template("email_template.html")

@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailRequest):
    # Render the email body using Jinja
    html_content = template.render(
        recipient_name=payload.recipient_name,
        subject=payload.subject,
        candidates=payload.candidates
    )

    # ✅ Use hardcoded sender details (working ones)
    from_email = "pst@emails.testbook.com"
    from_name = "PST Team"

    # Prepare the payload
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

    # Read API creds from Render environment
    api_key = os.getenv("EMAIL_API_KEY")
    api_url = os.getenv("EMAIL_API_URL")

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key
    }

    # Send request via Netcore
    session = requests.Session()
    req = requests.Request("POST", api_url, headers=headers, json=data)
    prepped = session.prepare_request(req)

    # Logging for debugging
    print("✅ Received payload:", payload.dict())
    print("📬 From Email:", from_email)
    print("📬 From Name:", from_name)
    print("📦 Final Netcore Payload:", data)
    print("🚀 Prepared Headers Sent:", prepped.headers)

    # Fire the request
    response = session.send(prepped)

    print("📨 Netcore Status:", response.status_code)
    print("📨 Netcore Response:", response.text)

    return {
        "status": "✅ Email API response" if response.status_code == 202 else "❌ Failed to send",
        "details": response.text
    }
