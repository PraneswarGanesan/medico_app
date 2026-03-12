import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def call_email_lambda(action: str, to_email: str, context: dict):
    """
    Call the serverless email Lambda function (via serverless-offline or AWS).
    action: 'SIGNUP_WELCOME' | 'BOOKING_CONFIRMATION'
    """
    payload = {
        "action": action,
        "to_email": to_email,
        "context": context,
    }
    endpoint = getattr(settings, 'EMAIL_LAMBDA_ENDPOINT', 'http://localhost:3000/email/send')
    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Email Lambda called successfully: {action} → {to_email}")
        return response.json()
    except requests.exceptions.ConnectionError:
        logger.warning(f"Email Lambda not reachable at {endpoint}. Skipping email: {action}")
    except requests.exceptions.Timeout:
        logger.warning("Email Lambda timed out.")
    except Exception as e:
        logger.error(f"Email Lambda error: {e}")
    return None


def create_google_calendar_event(user, title, start_dt, end_dt, description=""):
    """
    Create a Google Calendar event for the given user.
    Returns the event ID or None.
    Requires user.google_calendar_token to be set.
    """
    if not user.google_calendar_token:
        logger.info(f"No Google Calendar token for {user.username}. Skipping calendar event.")
        return None

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    try:
        creds = Credentials(
            token=user.google_calendar_token,
            refresh_token=user.google_calendar_refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )
        service = build('calendar', 'v3', credentials=creds)
        event = {
            'summary': title,
            'description': description,
            'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'UTC'},
            'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'UTC'},
        }
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        # Save updated token back
        user.google_calendar_token = creds.token
        user.save(update_fields=['google_calendar_token'])
        return created_event.get('id')
    except Exception as e:
        logger.error(f"Google Calendar error for {user.username}: {e}")
        return None
