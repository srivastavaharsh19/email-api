from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional, Union
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
import requests
import os

app = FastAPI()

# CORS setup (allow your Netlify domain)
origins = ["https://chic-klepon-77ad14.netlify.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Jinja2 template directory
env = Environment(loader=FileSystemLoader("templates"))

# Models
class Candidate(BaseModel):
    Name: str
    College: str
    Degree: str
    Skills: Union[str, List[str]]
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

    # Normalize skills field to comma-separated string
    for c in payload.candidates:
        if isinstance(c.Skills, list):
            c.Skills = ", ".join(c.Skills)

    # Render HTML content
    template = env.get_template("email_template.html")
    html_content = template.render(
        recipient_name=payload.recipient_name,
        candidates=payload.candidates
    )

    # HARDCODE sender email (known to work from earlier email)
    from_email = "connect@emails.testbook.com"
    from_name = "PST Team"

    print("📬 From Email:", repr(from_email))
    print("📬 From Name:", repr(from_name))

    # Netcore payload structure
    netcore_payload = {
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
            "email": from_email.strip(),
            "name": from_name.strip()
        },
        "content": [
            {
                "type": "html",
                "value": html_content
            }
        ]
    }

    print("📦 Final Netcore Payload:")
    print(netcore_payload)

    # Read environment variables (API key and URL)
    email_api_url = os.environ.get("EMAIL_API_URL")
    email_api_key = os.environ.get("EMAIL_API_KEY")

    headers = {
        "Content-Type": "application/json",
        "api_key": email_api_key
    }

    response = requests.post(email_api_url, headers=headers, json=netcore_payload)

    print("📨 Netcore Status:", response.status_code)
    print("📨 Netcore Response:", response.text)

    if response.status_code == 200:
        return {"status": "Email sent ✅"}
    else:
        return {"status": "❌ Failed to send", "details": response.text}
