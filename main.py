from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
import requests

app = FastAPI()

class Candidate(BaseModel):
    Name: str
    College: str
    Degree: str
    Skills: str
    Coding_Hours: str
    Projects: str
    LinkedIn: Optional[str]
    Portfolio: Optional[str]
    Email: str

class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: List[Candidate]

@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailRequest):
    # Compose your email HTML using payload.candidates
    # Call Netcore API (using requests.post) here to send the email
    return {"status": "Email sent"}
