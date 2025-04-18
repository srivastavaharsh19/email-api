from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
import requests
import os

app = FastAPI()

# Allow CORS for local or frontend app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Jinja2 environment
env = Environment(loader=FileSystemLoader("templates"))

# Pydantic models
class Candidate(BaseModel):
    Name: str
    College: str
    Degree: str
    Skills: str
    Coding_Hours: str
    Projects: str
    LinkedIn: Optional[str] = None
    Portfolio: Optional[str] = None
    Email: Optional[str] = None

class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: List[Candidate]

@app.post("/send_candidate_list_email/")
async def send_email(request: Request):
    body = await request.body()
    print("📦 RAW BODY RECEIVED:")
    print(body.decode("utf-8"))

    return {"status": "received"}

    # Render the HTML content
    template = env.get_template("email_template.html")
    html_content = template.render(
        recipient_name=payload.recipient_name,
        candidates=payload.candidates
    )

    # Read environment variables
    email_api_url = os.environ.get("EMAIL_API_URL")
    email_api_key = os.environ.get("EMAIL_API_KEY")
    from_email = os.environ.get("FROM_EMAIL")
    from_name = os.environ.get("FROM_NAME")

    # Construct Netcore request
    netcore_payload = {
        "from": {
            "email": from_email,
            "name": from_name
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
                "type": "html",
                "value": html_content
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "api_key": email_api_key
    }

    response = requests.post(email_api_url, json=netcore_payload, headers=headers)

    if response.status_code in [200, 202]:
        return {"status": "Email sent"}
    else:
        return {
            "status": "Failed to send email",
            "response_code": response.status_code,
            "details": response.text
        }
