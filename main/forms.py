from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, DoctorProfile, PatientProfile, AvailabilitySlot, Appointment


class DoctorSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    specialization = forms.ChoiceField(choices=DoctorProfile.SPECIALIZATION_CHOICES)
    qualification = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g. MBBS, MD'}))
    experience_years = forms.IntegerField(min_value=0, initial=0)
    consultation_fee = forms.DecimalField(max_digits=8, decimal_places=2, min_value=0, initial=0)
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Short bio...'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'doctor'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            DoctorProfile.objects.create(
                user=user,
                specialization=self.cleaned_data['specialization'],
                qualification=self.cleaned_data.get('qualification', ''),
                experience_years=self.cleaned_data.get('experience_years', 0),
                consultation_fee=self.cleaned_data.get('consultation_fee', 0),
                bio=self.cleaned_data.get('bio', ''),
            )
        return user


class PatientSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    blood_group = forms.ChoiceField(choices=[('', '-- Select --')] + list(PatientProfile.BLOOD_GROUP_CHOICES), required=False)
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Address...'}))
    emergency_contact = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'placeholder': 'Emergency Contact'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            PatientProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                blood_group=self.cleaned_data.get('blood_group', ''),
                address=self.cleaned_data.get('address', ''),
                emergency_contact=self.cleaned_data.get('emergency_contact', ''),
            )
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class AvailabilitySlotForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlot
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")
        return cleaned_data


class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Reason for visit (optional)...'}),
        }


class DoctorProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'qualification', 'experience_years', 'consultation_fee', 'bio']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            self.fields['phone'].initial = self.user.phone

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            self.user.phone = self.cleaned_data['phone']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile


class PatientProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = PatientProfile
        fields = ['date_of_birth', 'blood_group', 'address', 'emergency_contact', 'medical_history']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'medical_history': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            self.fields['phone'].initial = self.user.phone

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            self.user.phone = self.cleaned_data['phone']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile
