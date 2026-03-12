from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, DoctorProfile, PatientProfile, AvailabilitySlot, Appointment


class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name_plural = 'Doctor Profile'


class PatientProfileInline(admin.StackedInline):
    model = PatientProfile
    can_delete = False
    verbose_name_plural = 'Patient Profile'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('HMS Info', {'fields': ('role', 'phone')}),
    )

    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        if obj.role == 'doctor':
            return [DoctorProfileInline]
        elif obj.role == 'patient':
            return [PatientProfileInline]
        return []


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_booked')
    list_filter = ('is_booked', 'date', 'doctor')
    search_fields = ('doctor__username', 'doctor__first_name', 'doctor__last_name')
    date_hierarchy = 'date'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'get_doctor', 'get_date', 'status', 'created_at')
    list_filter = ('status', 'slot__date')
    search_fields = ('patient__username', 'slot__doctor__username')

    def get_doctor(self, obj):
        return obj.slot.doctor.get_full_name() or obj.slot.doctor.username
    get_doctor.short_description = 'Doctor'

    def get_date(self, obj):
        return obj.slot.date
    get_date.short_description = 'Date'
