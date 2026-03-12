from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


class DoctorRequiredMixin(LoginRequiredMixin):
    """Mixin to restrict access to doctors only."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_doctor():
            raise PermissionDenied("You must be a doctor to access this page.")
        return super().dispatch(request, *args, **kwargs)


class PatientRequiredMixin(LoginRequiredMixin):
    """Mixin to restrict access to patients only."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_patient():
            raise PermissionDenied("You must be a patient to access this page.")
        return super().dispatch(request, *args, **kwargs)
