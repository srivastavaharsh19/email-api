from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
import requests
import os

app = FastAPI()

# CORS
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

# Jinja2 template setup
env = Environment(loader=FileSystemLoader("templates"))

# Pydantic Models
class Candidate(BaseModel):
    Name: str
    College: str
    Degree: str
    Skills: List[str]
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

    try:
        template = env.get_template("email_template.html")
        html_content = template.render(
            recipient_name=payload.recipient_name,
            subject=payload.subject,
            candidates=payload.candidates
        )

        # HARDCODED FROM EMAIL AND NAME
        from_email = "pst@emails.testbook.com"
        from_name = "PST Team"

        # Compose final payload
        final_payload = {
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

        print("📬 From Email:", from_email)
        print("📬 From Name:", from_name)
        print("📦 Final Netcore Payload:")
        print(final_payload)

        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": os.environ.get("EMAIL_API_KEY")
        }

        response = requests.post(
            os.environ.get("EMAIL_API_URL"),
            headers=headers,
            json=final_payload
        )

        print("📨 Netcore Status:", response.status_code)
        print("📨 Netcore Response:", response.text)

        return {
            "status": "✅ Sent" if response.status_code == 200 else "❌ Failed to send",
            "details": response.text
        }

    except Exception as e:
        print("❌ Exception in /send_candidate_list_email/:", str(e))
        return {
            "status": "❌ Error",
            "message": str(e)
        }
