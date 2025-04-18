from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
import requests
import os
import json

app = FastAPI()

# ✅ Netlify domain (no trailing slash!)
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

# ✅ Jinja2 template
env = Environment(loader=FileSystemLoader("templates"))

# ✅ Models
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

    # ✅ Hardcoded and stripped sender details
    from_email = "pst@emails.testbook.com".strip()
    from_name = "PST Team".strip()

    print("📬 From Email:", from_email)
    print("📬 From Name:", from_name)

    # ✅ Convert skills to CSV string if needed
    for candidate in payload.candidates:
        if isinstance(candidate.Skills, list):
            candidate.Skills = ", ".join(candidate.Skills)

    # ✅ Render email HTML
    template = env.get_template("email_template.html")
    html_content = template.render(
        recipient_name=payload.recipient_name,
        candidates=payload.candidates
    )

    # ✅ Load environment variables (in case we switch later)
    email_api_url = os.environ.get("EMAIL_API_URL")
    email_api_key = os.environ.get("EMAIL_API_KEY")

    # ✅ Netcore-compliant payload
    netcore_payload = {
        "personalizations": [
            {
                "to": [
                    {
                        "email": payload.recipient_email.strip(),
                        "name": payload.recipient_name.strip()
                    }
                ],
                "subject": payload.subject.strip()
            }
        ],
        "from": {
            "email": str(from_email),
            "name": str(from_name)
        },
        "content": [
            {
                "type": "html",  # ✅ Netcore expects "html" or "amp-content"
                "value": html_content
            }
        ]
    }

    # ✅ Log final payload
    print("📦 Final Netcore Payload:")
    print(json.dumps(netcore_payload, indent=2))

    headers = {
        "Content-Type": "application/json",
        "api_key": email_api_key
    }

    try:
        response = requests.post(email_api_url, headers=headers, json=netcore_payload)
        print("📨 Netcore Status:", response.status_code)
        print("📨 Netcore Response:", response.text)

        if response.status_code == 200:
            return {"status": "✅ Email sent successfully"}
        else:
            return {
                "status": "❌ Failed to send",
                "details": response.text
            }
    except Exception as e:
        print("🔥 Exception occurred:", str(e))
        return {
            "status": "❌ Error",
            "message": str(e)
        }
