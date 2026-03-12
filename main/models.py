from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=15, blank=True)
    google_calendar_token = models.TextField(blank=True, null=True)
    google_calendar_refresh_token = models.TextField(blank=True, null=True)

    def is_doctor(self):
        return self.role == 'doctor'

    def is_patient(self):
        return self.role == 'patient'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"


class DoctorProfile(models.Model):
    SPECIALIZATION_CHOICES = (
        ('general', 'General Physician'),
        ('cardiology', 'Cardiology'),
        ('dermatology', 'Dermatology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics'),
        ('psychiatry', 'Psychiatry'),
        ('surgery', 'Surgery'),
        ('gynecology', 'Gynecology'),
        ('ophthalmology', 'Ophthalmology'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES, default='general')
    qualification = models.CharField(max_length=200, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"


class PatientProfile(models.Model):
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    medical_history = models.TextField(blank=True)

    def __str__(self):
        return f"Patient: {self.user.get_full_name() or self.user.username}"


class AvailabilitySlot(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots',
                               limit_choices_to={'role': 'doctor'})
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['doctor', 'date', 'start_time']

    def is_available(self):
        slot_datetime = timezone.datetime.combine(self.date, self.start_time)
        slot_datetime = timezone.make_aware(slot_datetime)
        return not self.is_booked and slot_datetime > timezone.now()

    def __str__(self):
        return f"Dr. {self.doctor.get_full_name()} | {self.date} {self.start_time}–{self.end_time}"


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments',
                                limit_choices_to={'role': 'patient'})
    slot = models.OneToOneField(AvailabilitySlot, on_delete=models.CASCADE, related_name='appointment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    doctor_calendar_event_id = models.CharField(max_length=255, blank=True)
    patient_calendar_event_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return (f"Appointment: {self.patient.get_full_name()} with "
                f"Dr. {self.slot.doctor.get_full_name()} on {self.slot.date}")
