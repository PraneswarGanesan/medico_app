from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────
    path('', views.HomeView.as_view(), name='home'),
    path('signup/doctor/', views.DoctorSignUpView.as_view(), name='signup_doctor'),
    path('signup/patient/', views.PatientSignUpView.as_view(), name='signup_patient'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),

    # ── Doctor ────────────────────────────────────────────────────────────
    path('doctor/dashboard/', views.DoctorDashboardView.as_view(), name='doctor_dashboard'),
    path('doctor/slots/', views.SlotListView.as_view(), name='slot_list'),
    path('doctor/slots/add/', views.SlotCreateView.as_view(), name='slot_create'),
    path('doctor/slots/<int:pk>/edit/', views.SlotUpdateView.as_view(), name='slot_edit'),
    path('doctor/slots/<int:pk>/delete/', views.SlotDeleteView.as_view(), name='slot_delete'),
    path('doctor/appointments/', views.DoctorAppointmentsView.as_view(), name='doctor_appointments'),
    path('doctor/profile/', views.DoctorProfileView.as_view(), name='doctor_profile'),

    # ── Patient ───────────────────────────────────────────────────────────
    path('patient/dashboard/', views.PatientDashboardView.as_view(), name='patient_dashboard'),
    path('patient/doctors/', views.DoctorListView.as_view(), name='doctor_list'),
    path('patient/doctors/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
    path('patient/book/<int:slot_pk>/', views.BookAppointmentView.as_view(), name='book_appointment'),
    path('patient/appointments/', views.PatientAppointmentsView.as_view(), name='patient_appointments'),
    path('patient/appointments/<int:pk>/cancel/', views.CancelAppointmentView.as_view(), name='cancel_appointment'),
    path('patient/profile/', views.PatientProfileView.as_view(), name='patient_profile'),
]
