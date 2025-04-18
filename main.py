from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
import requests
import os

app = FastAPI()

# Allow CORS from any origin (for Bolt or frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Jinja2 Environment
env = Environment(loader=FileSystemLoader("templates"))

# Candidate model
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

# Request body model
class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: List[Candidate]

@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailRequest):
    # Render the email HTML using Jinja2
    template = env.get_template("email_template.html")
    html_content = template.render(
        recipient_name=payload.recipient_name,
        candidates=payload.candidates
    )

    # --- Replace this with actual Netcore API call ---
    netcore_api_url = "https://api.netcore.example/send"  # Change this!
    response = requests.post(netcore_api_url, json={
        "to": payload.recipient_email,
        "subject": payload.subject,
        "body": html_content,
        "type": "html"
    })

    if response.status_code == 200:
        return {"status": "Email sent"}
    else:
        return {"status": "Failed to send", "details": response.text}
