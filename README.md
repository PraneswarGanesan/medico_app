# 🏥 Medico — Mini Hospital Management System

A full-stack **Hospital Management Web Application** built with Django where doctors can manage their availability and patients can book appointments seamlessly. Features a complete authentication system with **role-based access control**, automatic profile creation, session management, **Google Calendar integration**, and a **Serverless Email Notification Service** using AWS Lambda.

---

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running the Server](#running-the-server)
- [App Overview](#app-overview)
- [Serverless Email Service](#serverless-email-service)
- [Google Calendar Integration](#google-calendar-integration)
- [Race Condition Prevention](#race-condition-prevention)
- [Configuration](#configuration)
- [License](#license)

---

## 📌 About the Project

**Medico HMS** is a modern hospital management platform that connects doctors and patients. Doctors can sign up, set their availability time slots, and manage bookings. Patients can browse doctors by specialization, book available slots in real time, and receive instant email confirmations — all wrapped in a clean, responsive UI built with a natural green palette.

---

## ✨ Features

### 🔐 Authentication & Security
- Separate sign up & login for **Doctors** and **Patients**
- Passwords stored securely using Django's built-in hashing
- **Role-based access control** — doctors cannot access patient-only pages and vice versa
- Session-based authentication with `DoctorRequiredMixin` and `PatientRequiredMixin`

### 👨‍⚕️ Doctor Features
- Doctor dashboard with stats — upcoming slots, today's appointments, total appointments
- **Create, Update, Delete** availability slots by date & time
- View all patient bookings in one place
- Update professional profile — specialization, qualification, experience, fee, bio

### 🧑‍🦯 Patient Features
- Patient dashboard with upcoming and past appointments
- **Browse doctors** by specialization with filter support
- View doctor profiles — qualifications, experience, consultation fee
- **Book appointments** from available slots in real time
- Cancel confirmed appointments
- Update personal profile — blood group, DOB, address, emergency contact

### 📅 Smart Booking
- Only future, unbooked slots are shown to patients
- **Race condition prevention** using `select_for_update()` inside `transaction.atomic()` — no double bookings ever
- Slot is instantly marked as booked after confirmation

### 📬 Email Notifications (Serverless)
- Separate **Python Lambda function** using Serverless Framework
- Sends **Welcome Email** on signup
- Sends **Booking Confirmation Email** to both doctor and patient on appointment
- Runs locally via `serverless-offline` for development

### 🗓️ Google Calendar Integration
- On booking confirmation, events are automatically created in:
  - Doctor's Google Calendar
  - Patient's Google Calendar
- Uses Google Calendar API with OAuth2

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Django 5.0 |
| Frontend | HTML5, CSS3, JavaScript |
| Templating | Django Template Engine |
| Database | PostgreSQL |
| ORM | Django ORM |
| Authentication | Django Auth + Custom CBV Mixins |
| Email Service | AWS Lambda + Serverless Framework + Gmail SMTP |
| Calendar | Google Calendar API (OAuth2) |
| Static Files | Django Staticfiles |
| Views | 100% Class-Based Views (CBV) |

---

## 📁 Project Structure

```
medico_project/
│
├── main/                            # Core app
│   ├── migrations/                  # Database migrations
│   ├── templates/main/              # App-level HTML templates
│   │   ├── layout.html              # Base template (extended by all pages)
│   │   ├── home.html                # Landing page
│   │   ├── login.html               # Login page
│   │   ├── signup_doctor.html       # Doctor registration
│   │   ├── signup_patient.html      # Patient registration
│   │   ├── doctor_dashboard.html    # Doctor dashboard
│   │   ├── patient_dashboard.html   # Patient dashboard
│   │   ├── slot_list.html           # Doctor's slot management
│   │   ├── slot_form.html           # Create / edit slot
│   │   ├── slot_confirm_delete.html # Delete slot confirmation
│   │   ├── doctor_appointments.html # Doctor's appointment list
│   │   ├── doctor_list.html         # Patient browses doctors
│   │   ├── doctor_detail.html       # Doctor profile + available slots
│   │   ├── book_appointment.html    # Booking confirmation page
│   │   ├── patient_appointments.html# Patient's booking history
│   │   └── profile.html             # Shared profile edit page
│   ├── admin.py                     # Admin panel configuration
│   ├── apps.py
│   ├── forms.py                     # All Django forms
│   ├── mixins.py                    # DoctorRequiredMixin, PatientRequiredMixin
│   ├── models.py                    # User, DoctorProfile, PatientProfile,
│   │                                # AvailabilitySlot, Appointment
│   ├── urls.py                      # All URL routes
│   ├── utils.py                     # Email Lambda caller, Google Calendar helper
│   └── views.py                     # All CBV views
│
├── medico/                          # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── serverless_email/                # Serverless email service
│   ├── handler.py                   # Lambda function — sends emails
│   ├── serverless.yml               # Serverless Framework config
│   └── package.json                 # Node dependencies
│
├── static/
│   ├── css/main.css                 # Full stylesheet
│   └── js/main.js                   # JS utilities
│
├── .env.example                     # Environment variable template
├── manage.py
└── requirements.txt
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip
- PostgreSQL (installed and running)
- Node.js 18+ (for serverless email service)
- A valid Gmail account (for email notifications)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/medico-hms.git
cd medico-hms/medico_project
```

**2. Create and activate a virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install Python dependencies**

```bash
pip install Django==5.0.6 requests google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv
pip install psycopg2-binary --only-binary=:all:
```

**4. Create PostgreSQL database**

```bash
psql -U postgres
```
```sql
CREATE DATABASE medico_db;
\q
```

**5. Set up environment variables** *(see below)*

**6. Apply migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

**7. Create a superuser** *(optional, for admin access)*

```bash
python manage.py createsuperuser
```

### Environment Variables

Create a `.env` file in the `medico_project/` root directory:

```env
# Database
DB_NAME=medico_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

# Serverless Email Lambda
EMAIL_LAMBDA_ENDPOINT=http://localhost:3000/email/send

# Google Calendar OAuth2
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_secret

# SMTP (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_gmail@gmail.com
SMTP_PASSWORD=your_16_char_app_password
FROM_EMAIL=your_gmail@gmail.com
```

> ⚠️ For Gmail, use an **App Password** — not your regular Gmail password. Enable 2FA in your Google account, then generate one at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).

### Running the Server

**Terminal 1 — Django app:**
```bash
python manage.py runserver
```

**Terminal 2 — Serverless email service:**
```bash
cd serverless_email
npm install
npx serverless offline
```

Visit `http://127.0.0.1:8000/` in your browser.

Admin panel: `http://127.0.0.1:8000/admin/`

---

## 🗺️ App Overview

| URL Pattern | Page / Action | Role Required |
|---|---|---|
| `/` | Landing page | ❌ |
| `/signup/doctor/` | Doctor registration | ❌ |
| `/signup/patient/` | Patient registration | ❌ |
| `/login/` | Login | ❌ |
| `/logout/` | Logout | ✅ |
| `/doctor/dashboard/` | Doctor dashboard | 🩺 Doctor |
| `/doctor/slots/` | Manage availability slots | 🩺 Doctor |
| `/doctor/slots/add/` | Add new slot | 🩺 Doctor |
| `/doctor/slots/<id>/edit/` | Edit slot | 🩺 Doctor |
| `/doctor/slots/<id>/delete/` | Delete slot | 🩺 Doctor |
| `/doctor/appointments/` | View all bookings | 🩺 Doctor |
| `/doctor/profile/` | Edit doctor profile | 🩺 Doctor |
| `/patient/dashboard/` | Patient dashboard | 🧑 Patient |
| `/patient/doctors/` | Browse all doctors | 🧑 Patient |
| `/patient/doctors/<id>/` | Doctor detail + slots | 🧑 Patient |
| `/patient/book/<slot_id>/` | Book appointment | 🧑 Patient |
| `/patient/appointments/` | My bookings | 🧑 Patient |
| `/patient/appointments/<id>/cancel/` | Cancel appointment | 🧑 Patient |
| `/patient/profile/` | Edit patient profile | 🧑 Patient |

---

## 📬 Serverless Email Service

A separate **Python serverless function** handles all email sending. It runs independently from Django.

### Supported Actions

| Action | Triggered When | Sent To |
|---|---|---|
| `SIGNUP_WELCOME` | Doctor or Patient signs up | New user |
| `BOOKING_CONFIRMATION` | Appointment is booked | Both doctor & patient |

### Running Locally

```bash
cd serverless_email
npm install
npx serverless offline
# Starts on http://localhost:3000
```

### Test manually

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

> If the email service is not running, the Django app continues to work normally — emails are silently skipped without any errors.

---

## 🗓️ Google Calendar Integration

When an appointment is confirmed, calendar events are automatically created for both the doctor and patient.

### Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → Enable **Google Calendar API**
3. Go to **APIs & Services → Credentials → Create OAuth 2.0 Client ID**
4. Copy `Client ID` and `Client Secret` into your `.env` file

> If Google Calendar tokens are not configured for a user, calendar events are silently skipped without any errors.

---

## 🛡️ Race Condition Prevention

Slot booking uses `select_for_update()` inside `transaction.atomic()` to prevent two patients from booking the same slot simultaneously:

```python
@transaction.atomic
def form_valid(self, form):
    slot = AvailabilitySlot.objects.select_for_update().get(pk=self.slot.pk)
    if slot.is_booked:
        messages.error(request, "Sorry, this slot was just booked.")
        return redirect(...)
    slot.is_booked = True
    slot.save()
    ...
```

---

## ⚙️ Configuration

For **production** deployment, update `settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = 'your-strong-random-secret-key'
```

Then collect static files:

```bash
python manage.py collectstatic
```

---

## 🎨 Design

| Detail | Value |
|---|---|
| Primary Color | `#A5C89E` Sage Green |
| Secondary Color | `#FFFBB1` Soft Yellow |
| Accent Color | `#D8E983` Lime |
| Dark Accent | `#AEB877` Olive |
| Heading Font | DM Serif Display |
| Body Font | DM Sans |
| Views Pattern | 100% Class-Based Views (CBV) |
| Templates | DRY — all extend `layout.html` |

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

> Built with 🌿 and Django — because healthcare deserves great technology.
