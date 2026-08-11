from django import forms
from .models import Client, Clinic, StaffMembership , Service , Appointment 
from accounts.models import User
class ClinicForm(forms.ModelForm):
    class Meta:
        model = Clinic
        fields = [
            "name",
            # "email",
            "phone",
            "website",
            "address",
            "logo",
        ]

class StaffMembershipForm(forms.ModelForm):
    class Meta:
        model = StaffMembership
        fields = [
            "user",
            "role",
            "is_active",
        ]

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "gender",
            "dob",
            "address",
        ]

class ServiceForm(forms.ModelForm):

    class Meta:
        model = Service

        fields = [
            "name",
            "description",
            "duration",
            "price",
            "is_active",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),

            "duration": forms.NumberInput(
                attrs={
                    "min": 5,
                    "placeholder": "Duration in minutes",
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        price = cleaned_data.get("price")
        duration = cleaned_data.get("duration")

        if price is not None and price <= 0:
            raise forms.ValidationError(
                "Price must be greater than 0."
            )

        if duration is not None and duration <= 0:
            raise forms.ValidationError(
                "Duration must be greater than 0."
            )

        return cleaned_data


class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment

        fields = [
            "client",
            "service",
            "staff",
            "appointment_datetime",
            "status",
            "notes",
        ]

        widgets = {
            "appointment_datetime": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local"
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "rows": 3
                }
            ),
        }

    def __init__(self, *args, clinic=None, **kwargs):
        super().__init__(*args, **kwargs)

        if clinic:

            self.fields["client"].queryset = clinic.clients.all()

            self.fields["service"].queryset = clinic.services.filter(
                is_active=True
            )

            self.fields["staff"].queryset = StaffMembership.objects.filter(
                clinic=clinic
            ).select_related("user")