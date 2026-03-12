from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    TemplateView, CreateView, FormView, ListView,
    DetailView, UpdateView, DeleteView, View
)

from .forms import (
    DoctorSignUpForm, PatientSignUpForm, LoginForm,
    AvailabilitySlotForm, AppointmentBookingForm,
    DoctorProfileUpdateForm, PatientProfileUpdateForm,
)
from .mixins import DoctorRequiredMixin, PatientRequiredMixin
from .models import User, AvailabilitySlot, Appointment, DoctorProfile, PatientProfile
from .utils import call_email_lambda, create_google_calendar_event


# ─────────────────────────────────────────────
# Landing & Auth
# ─────────────────────────────────────────────

class HomeView(TemplateView):
    template_name = 'main/home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_doctor():
                return redirect('doctor_dashboard')
            return redirect('patient_dashboard')
        return super().get(request, *args, **kwargs)


class DoctorSignUpView(CreateView):
    form_class = DoctorSignUpForm
    template_name = 'main/signup_doctor.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        call_email_lambda(
            action='SIGNUP_WELCOME',
            to_email=user.email,
            context={
                'name': user.get_full_name() or user.username,
                'role': 'Doctor',
                'username': user.username,
            }
        )
        messages.success(self.request, "Doctor account created! Please log in.")
        return redirect(self.success_url)


class PatientSignUpView(CreateView):
    form_class = PatientSignUpForm
    template_name = 'main/signup_patient.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        call_email_lambda(
            action='SIGNUP_WELCOME',
            to_email=user.email,
            context={
                'name': user.get_full_name() or user.username,
                'role': 'Patient',
                'username': user.username,
            }
        )
        messages.success(self.request, "Patient account created! Please log in.")
        return redirect(self.success_url)


class UserLoginView(FormView):
    form_class = LoginForm
    template_name = 'main/login.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, f"Welcome back, {user.get_full_name() or user.username}!")
        if user.is_doctor():
            return redirect('doctor_dashboard')
        return redirect('patient_dashboard')


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect('home')


# ─────────────────────────────────────────────
# Doctor Views
# ─────────────────────────────────────────────

class DoctorDashboardView(DoctorRequiredMixin, TemplateView):
    template_name = 'main/doctor_dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        doctor = self.request.user
        today = timezone.now().date()
        ctx['upcoming_slots'] = AvailabilitySlot.objects.filter(
            doctor=doctor, date__gte=today
        ).select_related()
        ctx['upcoming_appointments'] = Appointment.objects.filter(
            slot__doctor=doctor, slot__date__gte=today, status='confirmed'
        ).select_related('patient', 'slot')
        ctx['total_appointments'] = Appointment.objects.filter(slot__doctor=doctor).count()
        ctx['today_appointments'] = Appointment.objects.filter(
            slot__doctor=doctor, slot__date=today, status='confirmed'
        ).count()
        return ctx


class SlotListView(DoctorRequiredMixin, ListView):
    template_name = 'main/slot_list.html'
    context_object_name = 'slots'
    paginate_by = 15

    def get_queryset(self):
        return AvailabilitySlot.objects.filter(doctor=self.request.user).order_by('date', 'start_time')


class SlotCreateView(DoctorRequiredMixin, CreateView):
    form_class = AvailabilitySlotForm
    template_name = 'main/slot_form.html'
    success_url = reverse_lazy('slot_list')

    def form_valid(self, form):
        slot = form.save(commit=False)
        slot.doctor = self.request.user
        slot.save()
        messages.success(self.request, "Availability slot created successfully!")
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['action'] = 'Create'
        return ctx


class SlotUpdateView(DoctorRequiredMixin, UpdateView):
    model = AvailabilitySlot
    form_class = AvailabilitySlotForm
    template_name = 'main/slot_form.html'
    success_url = reverse_lazy('slot_list')

    def get_queryset(self):
        return AvailabilitySlot.objects.filter(doctor=self.request.user, is_booked=False)

    def form_valid(self, form):
        messages.success(self.request, "Slot updated successfully!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['action'] = 'Update'
        return ctx


class SlotDeleteView(DoctorRequiredMixin, DeleteView):
    model = AvailabilitySlot
    template_name = 'main/slot_confirm_delete.html'
    success_url = reverse_lazy('slot_list')

    def get_queryset(self):
        return AvailabilitySlot.objects.filter(doctor=self.request.user, is_booked=False)

    def form_valid(self, form):
        messages.success(self.request, "Slot deleted.")
        return super().form_valid(form)


class DoctorAppointmentsView(DoctorRequiredMixin, ListView):
    template_name = 'main/doctor_appointments.html'
    context_object_name = 'appointments'
    paginate_by = 10

    def get_queryset(self):
        return Appointment.objects.filter(
            slot__doctor=self.request.user
        ).select_related('patient', 'slot').order_by('-slot__date', '-slot__start_time')


class DoctorProfileView(DoctorRequiredMixin, UpdateView):
    form_class = DoctorProfileUpdateForm
    template_name = 'main/profile.html'
    success_url = reverse_lazy('doctor_profile')

    def get_object(self):
        return get_object_or_404(DoctorProfile, user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['is_doctor'] = True
        return ctx


# ─────────────────────────────────────────────
# Patient Views
# ─────────────────────────────────────────────

class PatientDashboardView(PatientRequiredMixin, TemplateView):
    template_name = 'main/patient_dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        patient = self.request.user
        today = timezone.now().date()
        ctx['upcoming_appointments'] = Appointment.objects.filter(
            patient=patient, slot__date__gte=today, status='confirmed'
        ).select_related('slot__doctor', 'slot')
        ctx['past_appointments'] = Appointment.objects.filter(
            patient=patient, slot__date__lt=today
        ).select_related('slot__doctor', 'slot').order_by('-slot__date')[:5]
        ctx['total_appointments'] = Appointment.objects.filter(patient=patient).count()
        return ctx


class DoctorListView(PatientRequiredMixin, ListView):
    template_name = 'main/doctor_list.html'
    context_object_name = 'doctors'

    def get_queryset(self):
        qs = User.objects.filter(role='doctor').select_related('doctor_profile')
        specialization = self.request.GET.get('specialization', '')
        if specialization:
            qs = qs.filter(doctor_profile__specialization=specialization)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['specializations'] = DoctorProfile.SPECIALIZATION_CHOICES
        ctx['selected_specialization'] = self.request.GET.get('specialization', '')
        return ctx


class DoctorDetailView(PatientRequiredMixin, DetailView):
    model = User
    template_name = 'main/doctor_detail.html'
    context_object_name = 'doctor'

    def get_queryset(self):
        return User.objects.filter(role='doctor').select_related('doctor_profile')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.now().date()
        ctx['available_slots'] = AvailabilitySlot.objects.filter(
            doctor=self.object,
            date__gte=today,
            is_booked=False,
        ).order_by('date', 'start_time')
        return ctx


class BookAppointmentView(PatientRequiredMixin, FormView):
    form_class = AppointmentBookingForm
    template_name = 'main/book_appointment.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.slot = get_object_or_404(AvailabilitySlot, pk=kwargs['slot_pk'], is_booked=False)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['slot'] = self.slot
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        # Re-fetch with select_for_update to prevent race conditions
        slot = AvailabilitySlot.objects.select_for_update().get(pk=self.slot.pk)
        if slot.is_booked:
            messages.error(self.request, "Sorry, this slot was just booked by someone else.")
            return redirect('doctor_detail', pk=slot.doctor.pk)

        slot.is_booked = True
        slot.save()

        appointment = form.save(commit=False)
        appointment.patient = self.request.user
        appointment.slot = slot
        appointment.save()

        # Google Calendar integration
        doctor = slot.doctor
        patient = self.request.user
        start_dt = timezone.datetime.combine(slot.date, slot.start_time)
        start_dt = timezone.make_aware(start_dt)
        end_dt = timezone.datetime.combine(slot.date, slot.end_time)
        end_dt = timezone.make_aware(end_dt)

        doctor_event_id = create_google_calendar_event(
            user=doctor,
            title=f"Appointment with {patient.get_full_name() or patient.username}",
            start_dt=start_dt,
            end_dt=end_dt,
            description=appointment.reason,
        )
        patient_event_id = create_google_calendar_event(
            user=patient,
            title=f"Appointment with Dr. {doctor.get_full_name() or doctor.username}",
            start_dt=start_dt,
            end_dt=end_dt,
            description=appointment.reason,
        )
        if doctor_event_id:
            appointment.doctor_calendar_event_id = doctor_event_id
        if patient_event_id:
            appointment.patient_calendar_event_id = patient_event_id
        appointment.save()

        # Email notifications
        call_email_lambda(
            action='BOOKING_CONFIRMATION',
            to_email=patient.email,
            context={
                'patient_name': patient.get_full_name() or patient.username,
                'doctor_name': f"Dr. {doctor.get_full_name() or doctor.username}",
                'date': str(slot.date),
                'start_time': str(slot.start_time),
                'end_time': str(slot.end_time),
            }
        )
        call_email_lambda(
            action='BOOKING_CONFIRMATION',
            to_email=doctor.email,
            context={
                'patient_name': patient.get_full_name() or patient.username,
                'doctor_name': f"Dr. {doctor.get_full_name() or doctor.username}",
                'date': str(slot.date),
                'start_time': str(slot.start_time),
                'end_time': str(slot.end_time),
            }
        )

        messages.success(self.request, "Appointment booked successfully! 🎉")
        return redirect('patient_appointments')


class PatientAppointmentsView(PatientRequiredMixin, ListView):
    template_name = 'main/patient_appointments.html'
    context_object_name = 'appointments'
    paginate_by = 10

    def get_queryset(self):
        return Appointment.objects.filter(
            patient=self.request.user
        ).select_related('slot__doctor', 'slot__doctor__doctor_profile').order_by('-slot__date')


class CancelAppointmentView(PatientRequiredMixin, View):
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk, patient=request.user, status='confirmed')
        with transaction.atomic():
            appointment.status = 'cancelled'
            appointment.save()
            appointment.slot.is_booked = False
            appointment.slot.save()
        messages.success(request, "Appointment cancelled successfully.")
        return redirect('patient_appointments')


class PatientProfileView(PatientRequiredMixin, UpdateView):
    form_class = PatientProfileUpdateForm
    template_name = 'main/profile.html'
    success_url = reverse_lazy('patient_profile')

    def get_object(self):
        return get_object_or_404(PatientProfile, user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['is_doctor'] = False
        return ctx
