"""
Medico HMS — Serverless Email Lambda Function
Handles: SIGNUP_WELCOME, BOOKING_CONFIRMATION
Run locally: serverless offline
Deploy: serverless deploy
"""

import json
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@medico.com')
FROM_NAME = os.environ.get('FROM_NAME', 'Medico HMS')


# ─── Email Templates ─────────────────────────────────────────────────────────

TEMPLATES = {
    'SIGNUP_WELCOME': {
        'subject': 'Welcome to Medico HMS! 🌿',
        'html': """
        <div style="font-family:DM Sans,Arial,sans-serif;max-width:560px;margin:0 auto;background:#f8faf5;border-radius:12px;overflow:hidden;">
          <div style="background:linear-gradient(135deg,#A5C89E,#D8E983);padding:36px 32px;text-align:center;">
            <div style="font-size:2.5rem;">✦</div>
            <h1 style="font-size:1.8rem;margin:8px 0 0;color:#1e2a18;">Welcome to Medico!</h1>
          </div>
          <div style="padding:32px;background:#fff;">
            <p style="font-size:1rem;color:#1e2a18;">Hi <strong>{name}</strong>,</p>
            <p style="color:#6b7c63;line-height:1.7;">
              Your <strong>{role}</strong> account has been successfully created on Medico HMS.
              We're excited to have you on board!
            </p>
            <div style="background:#f0faf0;border:1.5px solid #A5C89E;border-radius:8px;padding:16px;margin:20px 0;">
              <p style="margin:0;font-size:0.9rem;color:#1e2a18;">
                <strong>Username:</strong> {username}
              </p>
            </div>
            <p style="color:#6b7c63;font-size:0.9rem;">
              {role_message}
            </p>
            <div style="text-align:center;margin-top:28px;">
              <a href="http://localhost:8000/login/" style="background:#7da877;color:#fff;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:700;font-size:0.95rem;">
                Sign In to Medico →
              </a>
            </div>
          </div>
          <div style="padding:16px;text-align:center;font-size:0.8rem;color:#6b7c63;background:#f8faf5;">
            Medico HMS — Healing with technology. &copy; 2024
          </div>
        </div>
        """,
    },
    'BOOKING_CONFIRMATION': {
        'subject': 'Appointment Confirmed — Medico HMS 📅',
        'html': """
        <div style="font-family:DM Sans,Arial,sans-serif;max-width:560px;margin:0 auto;background:#f8faf5;border-radius:12px;overflow:hidden;">
          <div style="background:linear-gradient(135deg,#D8E983,#FFFBB1);padding:36px 32px;text-align:center;">
            <div style="font-size:2.5rem;">📅</div>
            <h1 style="font-size:1.6rem;margin:8px 0 0;color:#1e2a18;">Appointment Confirmed!</h1>
          </div>
          <div style="padding:32px;background:#fff;">
            <p style="font-size:1rem;color:#1e2a18;">Your appointment has been successfully booked.</p>
            <div style="background:#f8faf5;border:2px solid #AEB877;border-radius:10px;padding:20px;margin:20px 0;">
              <table style="width:100%;border-collapse:collapse;font-size:0.9rem;">
                <tr style="border-bottom:1px solid #dde8d4;">
                  <td style="padding:8px 0;color:#6b7c63;">Patient</td>
                  <td style="padding:8px 0;font-weight:700;text-align:right;">{patient_name}</td>
                </tr>
                <tr style="border-bottom:1px solid #dde8d4;">
                  <td style="padding:8px 0;color:#6b7c63;">Doctor</td>
                  <td style="padding:8px 0;font-weight:700;text-align:right;">{doctor_name}</td>
                </tr>
                <tr style="border-bottom:1px solid #dde8d4;">
                  <td style="padding:8px 0;color:#6b7c63;">Date</td>
                  <td style="padding:8px 0;font-weight:700;text-align:right;">{date}</td>
                </tr>
                <tr>
                  <td style="padding:8px 0;color:#6b7c63;">Time</td>
                  <td style="padding:8px 0;font-weight:700;text-align:right;">{start_time} – {end_time}</td>
                </tr>
              </table>
            </div>
            <p style="color:#6b7c63;font-size:0.875rem;line-height:1.7;">
              Please arrive 10 minutes early. A calendar event has been added to your Google Calendar (if connected).
            </p>
            <div style="text-align:center;margin-top:24px;">
              <a href="http://localhost:8000/patient/appointments/" style="background:#7da877;color:#fff;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:700;font-size:0.95rem;">
                View My Appointments →
              </a>
            </div>
          </div>
          <div style="padding:16px;text-align:center;font-size:0.8rem;color:#6b7c63;background:#f8faf5;">
            Medico HMS — Healing with technology. &copy; 2024
          </div>
        </div>
        """,
    },
}

ROLE_MESSAGES = {
    'Doctor': (
        "You can now log in, set your availability slots, and manage patient appointments "
        "right from your dashboard."
    ),
    'Patient': (
        "You can now log in, browse available doctors, and book appointments in seconds."
    ),
}


# ─── Core Logic ──────────────────────────────────────────────────────────────

def build_email_body(action: str, context: dict) -> tuple[str, str]:
    """Return (subject, html_body) for the given action."""
    template = TEMPLATES.get(action)
    if not template:
        raise ValueError(f"Unknown email action: {action}")

    subject = template['subject']
    html = template['html']

    if action == 'SIGNUP_WELCOME':
        role = context.get('role', 'User')
        html = html.format(
            name=context.get('name', 'User'),
            role=role,
            username=context.get('username', ''),
            role_message=ROLE_MESSAGES.get(role, ''),
        )
    elif action == 'BOOKING_CONFIRMATION':
        html = html.format(
            patient_name=context.get('patient_name', ''),
            doctor_name=context.get('doctor_name', ''),
            date=context.get('date', ''),
            start_time=context.get('start_time', ''),
            end_time=context.get('end_time', ''),
        )

    return subject, html


def send_smtp_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send email via SMTP. Returns True on success."""
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured. Email skipped.")
        logger.info(f"[DRY RUN] Would send to: {to_email} | Subject: {subject}")
        return True  # Graceful skip in dev

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg['To'] = to_email

    text_body = subject  # Plain text fallback
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())

    logger.info(f"Email sent to {to_email} | Subject: {subject}")
    return True


def _response(status_code: int, body: dict) -> dict:
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(body),
    }


# ─── Lambda Handler ───────────────────────────────────────────────────────────

def send_email(event, context):
    """
    AWS Lambda handler.
    Expected JSON body:
    {
        "action": "SIGNUP_WELCOME" | "BOOKING_CONFIRMATION",
        "to_email": "user@example.com",
        "context": { ... }
    }
    """
    try:
        body = json.loads(event.get('body') or '{}')
    except json.JSONDecodeError:
        return _response(400, {'error': 'Invalid JSON body'})

    action = body.get('action')
    to_email = body.get('to_email')
    ctx = body.get('context', {})

    if not action or not to_email:
        return _response(400, {'error': 'Missing required fields: action, to_email'})

    try:
        subject, html_body = build_email_body(action, ctx)
        success = send_smtp_email(to_email, subject, html_body)
        if success:
            return _response(200, {'message': f'Email sent successfully to {to_email}'})
        else:
            return _response(500, {'error': 'Failed to send email'})
    except ValueError as e:
        return _response(400, {'error': str(e)})
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return _response(500, {'error': 'SMTP error', 'detail': str(e)})
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return _response(500, {'error': 'Internal server error', 'detail': str(e)})
