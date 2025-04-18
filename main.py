from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
import requests

app = FastAPI()

# CORS setup for Netlify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chic-klepon-77ad14.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Jinja2 template
env = Environment(loader=FileSystemLoader("templates"))

# Candidate data model
class Candidate(BaseModel):
    Name: str
    College: str
    Degree: str
    Skills: List[str] | str
    Coding_Hours: str
    Projects: str
    LinkedIn: Optional[str] = ""
    Portfolio: Optional[str] = ""
    Email: Optional[str] = ""

# Email input model
class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: List[Candidate]

@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailRequest):
    print("✅ Received payload:")
    print(payload.dict())

    # Format candidate skills list
    for c in payload.candidates:
        if isinstance(c.Skills, list):
            c.Skills = ", ".join(c.Skills)

    # Render HTML email
    template = env.get_template("email_template.html")
    html_content = template.render(
        recipient_name=payload.recipient_name,
        candidates=payload.candidates
    )

    # 🔐 HARDCODED values (100% valid format)
    from_email = "pst@emails.testbook.com"  # ✅ working sender
    from_name = "PST Team"  # ✅ working name

    # 🚀 Final Netcore API payload
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
            "email": from_email.strip(),  # 🔍 ensure no spaces
            "name": from_name.strip()
        },
        "content": [
            {
                "type": "html",  # ✅ NOT text/html, just html
                "value": html_content
            }
        ]
    }

    print("📦 Final Netcore Payload:")
    print(netcore_payload)

    headers = {
        "Content-Type": "application/json",
        "api_key": "12f88c25be606f95bf4cfee3d3f58746"  # ✅ still working key
    }

    response = requests.post(
        "https://emailapi.netcorecloud.net/v5.1/mail/send",
        headers=headers,
        json=netcore_payload
    )

    print("📨 Netcore Status:", response.status_code)
    print("📨 Netcore Response:", response.text)

    if response.status_code == 200:
        return {"status": "✅ Email sent successfully"}
    else:
        return {
            "status": "❌ Failed to send",
            "details": response.text
        }
