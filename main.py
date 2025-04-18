from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import requests
from jinja2 import Environment, BaseLoader

app = FastAPI()

# CORS config
origins = [
    "https://chic-klepon-77ad14.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email request body
class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    subject: str
    candidates: List[dict]

# POST route
@app.post("/send_candidate_list_email/")
async def send_email(payload: EmailRequest):
    print("✅ Received payload:")
    print(payload.dict())

    # ----- Email Config -----
    api_url = "https://emailapi.netcorecloud.net/v5.1/mail/send"
    api_key = "12f88c25be606f95bf4cfee3d3f58746"
    from_email = "pst@emails.testbook.com"
    from_name = "PST Team"

    # ----- Render HTML using Jinja2 -----
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>{{ subject }}</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          color: #333;
          line-height: 1.5;
        }
        h2 {
          color: #1a1a1a;
        }
        table {
          border-collapse: collapse;
          width: 100%;
          margin-top: 16px;
          font-size: 14px;
        }
        th, td {
          text-align: left;
          padding: 10px;
          border: 1px solid #ddd;
        }
        th {
          background-color: #f5f5f5;
        }
        a {
          color: #2a7ae2;
          text-decoration: none;
        }
        p.footer {
          margin-top: 24px;
        }
      </style>
    </head>
    <body>
      <h2>Hello {{ recipient_name }},</h2>
      <p>Here is the list of shortlisted candidates for your review:</p>

      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>College</th>
            <th>Degree</th>
            <th>Skills</th>
            <th>Coding Hours</th>
            <th>Projects</th>
            <th>LinkedIn</th>
            <th>Portfolio</th>
            <th>Email</th>
          </tr>
        </thead>
        <tbody>
          {% for c in candidates %}
          <tr>
            <td>{{ c.Name }}</td>
            <td>{{ c.College }}</td>
            <td>{{ c.Degree }}</td>
            <td>{{ ", ".join(c.Skills) }}</td>
            <td>{{ c.Coding_Hours }}</td>
            <td>{{ c.Projects }}</td>
            <td>{{ c.LinkedIn }}</td>
            <td>{{ c.Portfolio }}</td>
            <td>{{ c.Email }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>

      <p class="footer">
        Best regards,<br>
        <strong>Polaris Campus Team</strong>
      </p>
    </body>
    </html>
    """

    template = Environment(loader=BaseLoader()).from_string(html_template)
    html_content = template.render(
        recipient_name=payload.recipient_name,
        subject=payload.subject,
        candidates=payload.candidates
    )

    # ----- Prepare payload -----
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

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key
    }

    print("📦 Final Netcore Payload:")
    print(data)

    # ----- Send to Netcore -----
    try:
        response = requests.post(api_url, headers=headers, json=data)
        print(f"📨 Netcore Status: {response.status_code}")
        print(f"📨 Netcore Response: {response.text}")
        return {
            "status": "✅ Sent" if response.status_code == 200 else "❌ Failed to send",
            "details": response.text
        }

    except Exception as e:
        print(f"🔥 Exception in /send_candidate_list_email/: {str(e)}")
        return {"status": "❌ Error", "message": str(e)}
