# 🏥 Medico — Mini Hospital Management System

A full-featured hospital management web application built with **Django** (CBV-only), **PostgreSQL**, and a **Serverless email notification service** using AWS Lambda / serverless-offline.

---

## 📁 Project Structure

```
medico/                          ← Django project root
├── main/                        ← Core app
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py                 ← Admin panel configuration
│   ├── apps.py
│   ├── forms.py                 ← All Django forms
│   ├── mixins.py                ← DoctorRequiredMixin, PatientRequiredMixin
│   ├── models.py                ← User, DoctorProfile, PatientProfile, AvailabilitySlot, Appointment
│   ├── urls.py                  ← All URL routes
│   ├── utils.py                 ← Email Lambda caller, Google Calendar helper
│   └── views.py                 ← All CBV views
├── medico/                      ← Django settings package
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/
│   ├── css/main.css             ← Full stylesheet (palette: A5C89E, FFFBB1, D8E983, AEB877)
│   └── js/main.js
├── templates/
│   └── main/
│       ├── layout.html          ← Base template (DRY)
│       ├── home.html
│       ├── login.html
│       ├── signup_doctor.html
│       ├── signup_patient.html
│       ├── doctor_dashboard.html
│       ├── patient_dashboard.html
│       ├── slot_list.html
│       ├── slot_form.html
│       ├── slot_confirm_delete.html
│       ├── doctor_appointments.html
│       ├── doctor_list.html
│       ├── doctor_detail.html
│       ├── book_appointment.html
│       ├── patient_appointments.html
│       └── profile.html
├── serverless_email/            ← Serverless Lambda email service
│   ├── handler.py               ← Lambda function
│   ├── serverless.yml           ← Serverless Framework config
│   └── package.json
├── .env.example
├── manage.py
└── requirements.txt
```

---

## ⚙️ Setup Instructions

### 1. Clone & Virtual Environment

```bash
cd medico
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. PostgreSQL Database

```sql
-- In psql:
CREATE DATABASE medico_db;
CREATE USER postgres WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE medico_db TO postgres;
```

### 3. Environment Variables

```bash
cp .env.example .env
# Edit .env with your DB credentials, SMTP settings, Google OAuth keys
```

Update `medico/settings.py` `DATABASES` section with your credentials, or use `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run Django Server

```bash
python manage.py runserver
# Visit: http://localhost:8000
```

---

## 📬 Serverless Email Service (Local)

### Prerequisites
- Node.js 18+
- npm

### Setup

```bash
cd serverless_email
npm install
```

### Run Locally

```bash
npx serverless offline
# Starts on: http://localhost:3000
```

### Test It

```bash
curl -X POST http://localhost:3000/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "action": "SIGNUP_WELCOME",
    "to_email": "test@example.com",
    "context": {
      "name": "John Doe",
      "role": "Patient",
      "username": "johndoe"
    }
  }'
```

### Configure SMTP (Gmail)

1. Enable 2FA on your Gmail account.
2. Create an App Password: Google Account → Security → App Passwords.
3. Set in `.env`:
   ```
   SMTP_USER=your@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

---

## 🗓️ Google Calendar Integration

### Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com).
2. Create a project → Enable **Google Calendar API**.
3. Create OAuth 2.0 credentials → Download `client_secret.json`.
4. Add to `.env`:
   ```
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   ```

> **Note:** The current implementation in `utils.py` calls `create_google_calendar_event()`. To fully connect Google OAuth for each user, implement an OAuth flow (auth URL → callback → store token) using `google_auth_oauthlib`. The helper in `utils.py` is ready to use tokens once stored in `user.google_calendar_token`.

---

## 🔐 User Roles

| Feature | Doctor | Patient |
|---|---|---|
| Sign up / Login | ✅ | ✅ |
| Dashboard | ✅ | ✅ |
| Create/Edit/Delete Slots | ✅ | ❌ |
| View Patient Appointments | ✅ | ❌ |
| Browse Doctors | ❌ | ✅ |
| Book Appointments | ❌ | ✅ |
| Cancel Appointments | ❌ | ✅ |

---

## 🛡️ Race Condition Prevention

Slot booking uses `select_for_update()` inside a `transaction.atomic()` block to prevent double-booking:

```python
@transaction.atomic
def form_valid(self, form):
    slot = AvailabilitySlot.objects.select_for_update().get(pk=self.slot.pk)
    if slot.is_booked:
        messages.error(...)
        return redirect(...)
    slot.is_booked = True
    slot.save()
    ...
```

---

## 🎨 Design

- **Colors:** `#A5C89E` (sage), `#FFFBB1` (yellow), `#D8E983` (lime), `#AEB877` (olive)
- **Fonts:** DM Serif Display (headings) + DM Sans (body)
- **Architecture:** DRY with `layout.html` base template
- **Views:** 100% Class-Based Views (CBV)
