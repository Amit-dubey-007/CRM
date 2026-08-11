from django.db import models

# Create your models here.
class Clinic(models.Model):
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='clinics')
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    logo = models.ImageField(upload_to='clinic_logos/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name 

from django.conf import settings

class StaffMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        STAFF = "STAFF", "Staff"

    clinic = models.ForeignKey(
        "clinics.Clinic",
        on_delete=models.CASCADE,
        related_name="members"
    )

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STAFF,
        db_index=True
    )

    is_active = models.BooleanField(default=True)

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("clinic", "user")

        indexes = [
            models.Index(fields=["clinic"]),
            models.Index(fields=["clinic", "user"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.clinic.name} - {self.role}"

from django.conf import settings
from django.db import models

class Client(models.Model):
    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        OTHER = "OTHER", "Other"
        PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY", "Prefer not to say"

    clinic = models.ForeignKey(
        "clinics.Clinic",
        on_delete=models.CASCADE,
        related_name="clients"
    )

    first_name = models.CharField(max_length=100,db_index=True)
    last_name = models.CharField(max_length=100, blank=True,db_index=True)

    phone = models.CharField(max_length=15,db_index=True)
    email = models.EmailField(blank=True,db_index=True)

    gender = models.CharField(
        max_length=25,
        choices=Gender.choices,
        blank=True
    )

    dob = models.DateField(
        null=True,
        blank=True
    )

    address = models.TextField(blank=True)

    notes = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        indexes = [
            models.Index(fields=["clinic"]),
            models.Index(fields=["clinic", "first_name"]),
            models.Index(fields=["clinic", "last_name"]),
            models.Index(fields=["clinic", "phone"]),
        ]


class Service(models.Model):

    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name="services"
    )

    name = models.CharField(max_length=200,db_index=True)

    description = models.TextField(blank=True,db_index=True)

    duration = models.PositiveIntegerField(
        help_text="Duration in minutes"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    is_active = models.BooleanField(default=True,db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    class Meta:
        indexes = [
            models.Index(fields=["clinic"]),
            models.Index(fields=["clinic", "name"]),
        ]


class Appointment(models.Model):

    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        NO_SHOW = "NO_SHOW", "No Show"

    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    staff = models.ForeignKey(
        StaffMembership,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments"
    )

    appointment_datetime = models.DateTimeField(db_index=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        db_index=True
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "appointment_datetime"
        ]

    def __str__(self):
        return (
            f"{self.client} - "
            f"{self.service} - "
            f"{self.appointment_datetime}"
        )

    class Meta:
        indexes = [
            models.Index(fields=["clinic"]),
            models.Index(fields=["clinic", "appointment_datetime"]),
            models.Index(fields=["clinic", "status"]),
        ]