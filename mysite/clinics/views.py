from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

from .models import Client, Clinic, StaffMembership,Service,Appointment
from accounts.models import User

from .forms import ClinicForm,StaffMembershipForm,ClientForm,ServiceForm,AppointmentForm

@login_required
def create_clinic(request):
    if Clinic.objects.filter(owner=request.user).exists():
        return redirect("clinics:home")
    
    if request.method == "POST":
        form = ClinicForm(request.POST, request.FILES)

        if form.is_valid():
            clinic = form.save(commit=False)
            clinic.owner = request.user
            clinic.email = request.user.email  # Set the email to the logged-in user's email
            clinic.save()
            StaffMembership.objects.create(
                clinic=clinic,
                user=request.user,
                role=StaffMembership.Role.OWNER
            )

            return redirect("clinics:home")

    else:
        form = ClinicForm()

    return render(
        request,
        "clinics/create_clinic.html",
        {
            "form": form
        }
    )

def clinic_dashboard(request):
    # clinic = request.user.clinics.first()  # Assuming a user can have only one clinic
    # if not clinic:
    #     return redirect("clinics:create_clinic")  # Redirect to create clinic if none exists
    # return render(
    #     request,
    #     "clinics/clinic_dashboard.html",
    #     {
    #         "clinic": clinic
    #     }
    return redirect("clinics:home")

def edit_clinic(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)
    if clinic.owner != request.user:
        return redirect("clinics:home")  # Redirect if the user is not the owner of the clinic

    if request.method == "POST":
        form = ClinicForm(request.POST, request.FILES, instance=clinic)

        if form.is_valid():
            form.save()
            return redirect("clinics:home")

    else:
        form = ClinicForm(instance=clinic)

    return render(
        request,
        "clinics/edit_clinic.html",
        {
            "form": form,
            "clinic": clinic
        }
    )

def clinic_detail(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)
    return render(
        request,
        "clinics/clinic_detail.html",
        {
            "clinic": clinic
        }
    )

def delete_clinic(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)
    if clinic.owner != request.user:
        return redirect("clinics:home")  # Redirect if the user is not the owner of the clinic
    if request.method == "POST":
        clinic.delete()
        return redirect("clinics:home")
    return render(
        request,
        "clinics/delete_clinic.html",
        {
            "clinic": clinic
        }
    )

@login_required
def home(request):
    clinic = Clinic.objects.filter(owner=request.user).first()
    if clinic:
        return redirect("clinics:todays_dashboard")
    return redirect("clinics:create_clinic")

def add_staff(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)
    if clinic.owner != request.user:
        return redirect("clinics:home")  # Redirect if the user is not the owner of the clinic
    if request.method == "POST":
        form = StaffMembershipForm(request.POST)

        if form.is_valid():
            user = form.cleaned_data['user']
            if StaffMembership.objects.filter(clinic=clinic, user=user).exists():
                form.add_error('user', 'This user is already a staff member of this clinic.')
            else:
                staff_membership = form.save(commit=False)
                staff_membership.clinic = clinic
                staff_membership.save()
                return redirect("clinics:home")

    else:
        form = StaffMembershipForm()

    return render(
        request,
        "clinics/add_staff.html",
        {
            "form": form,
            "clinic": clinic
        }
    )

def remove_staff(request, clinic_id, staff_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)
    if clinic.owner != request.user:
        return redirect("clinics:home")  # Redirect if the user is not the owner of the clinic

    staff_membership = get_object_or_404(StaffMembership, id=staff_id, clinic=clinic)
    if staff_membership.user == request.user:
        return redirect("clinics:staff_list", clinic_id=clinic.id)  # Prevent the owner from removing themselves

    if request.method == "POST":
        staff_membership.delete()
        return redirect("clinics:staff_list", clinic_id=clinic.id)

    return render(
        request,
        "clinics/remove_staff.html",
        {
            "staff_membership": staff_membership,
            "clinic": clinic
        }
    )

def staff_list(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)
    if clinic.owner != request.user:
        return redirect("clinics:home")  # Redirect if the user is not the owner of the clinic

    q = request.GET.get("q", "").strip()

    staff = (
        StaffMembership.objects
        .filter(clinic=clinic)
        .select_related("user")
    )

    if q:
        staff = staff.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__email__icontains=q)
        )

    staff = staff.order_by("user__first_name", "user__last_name")


    return render(
        request,
        "clinics/staff_list.html",
        {
            "clinic": clinic,
            "staff_members": staff
        }
    )

def update_staff(request, clinic_id, staff_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)
    if clinic.owner != request.user:
        return redirect("clinics:home")  # Redirect if the user is not the owner of the clinic

    staff_membership = get_object_or_404(StaffMembership, id=staff_id, clinic=clinic)

    if request.method == "POST":
        form = StaffMembershipForm(request.POST, instance=staff_membership)

        if form.is_valid():
            form.save()
            return redirect("clinics:staff_list", clinic_id=clinic.id)

    else:
        form = StaffMembershipForm(instance=staff_membership)

    return render(
        request,
        "clinics/update_staff.html",
        {
            "form": form,
            "clinic": clinic,
            "staff_membership": staff_membership
        }
    )

def user_can_access_clinic(user, clinic):
    return (
        clinic.owner == user or
        StaffMembership.objects.filter(
            clinic=clinic,
            user=user
        ).exists()
    )

def add_client(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)

    if not user_can_access_clinic(request.user, clinic):
        return redirect("clinics:home")

    if request.method == "POST":
        form = ClientForm(request.POST)

        if form.is_valid():
            client = form.save(commit=False)
            client.clinic = clinic
            client.save()
            messages.success(request, "Client added successfully.")
            return redirect("clinics:client_list", clinic_id=clinic.id)

    else:
        form = ClientForm()

    return render(
        request,
        "clinics/add_client.html",
        {
            "form": form,
            "clinic": clinic
        }
    )

def update_client(request, clinic_id, client_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)
    client = get_object_or_404(Client, id=client_id, clinic=clinic)

    if not user_can_access_clinic(request.user, clinic):
        return redirect("clinics:home")

    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)

        if form.is_valid():
            form.save()
            messages.success(request, "Client updated successfully.")
            return redirect("clinics:client_list", clinic_id=clinic.id)

    else:
        form = ClientForm(instance=client)

    return render(
        request,
        "clinics/edit_client.html",
        {
            "form": form,
            "clinic": clinic,
            "client": client
        }
    )

def client_list(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)

    if not user_can_access_clinic(request.user, clinic):
        return redirect("clinics:home")

    q = request.GET.get("q", "").strip()

    clients = clinic.clients.filter(is_active=True)

    if q:
        clients = clients.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q)
        )

    clients = clients.order_by("-created_at")
    return render(
        request,
        "clinics/client_list.html",
        {
            "clinic": clinic,
            "clients": clients
        }
    )

def delete_client(request, clinic_id, client_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)
    client = get_object_or_404(Client, id=client_id, clinic=clinic)

    if not user_can_access_clinic(request.user, clinic):
        return redirect("clinics:home")

    if request.method == "POST":
        client.delete()
        messages.success(request, "Client deleted successfully.")
        return redirect("clinics:client_list", clinic_id=clinic.id)

    return render(
        request,
        "clinics/delete_client.html",
        {
            "clinic": clinic,
            "client": client
        }
    )


@login_required
def add_service(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)

    if not user_can_access_clinic(request.user, clinic):
        return redirect("clinics:home")

    if request.method == "POST":
        form = ServiceForm(request.POST)

        if form.is_valid():
            service = form.save(commit=False)
            service.clinic = clinic
            service.save()

            messages.success(request, "Service added successfully.")
            return redirect(
                "clinics:service_list",
                clinic_id=clinic.id
            )

    else:
        form = ServiceForm()

    return render(
        request,
        "clinics/add_service.html",
        {
            "form": form,
            "clinic": clinic,
        },
    )

@login_required
def service_list(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)

    if not user_can_access_clinic(request.user, clinic):
        return redirect("clinics:home")

    q = request.GET.get("q", "").strip()

    services = clinic.services.filter(is_active=True)

    if q:
        services = services.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )

    services = services.order_by("name")

    return render(
        request,
        "clinics/service_list.html",
        {
            "clinic": clinic,
            "services": services,
        },
    )

@login_required
def update_service(request, clinic_id, service_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)

    service = get_object_or_404(
        Service,
        id=service_id,
        clinic=clinic
    )

    if not user_can_access_clinic(request.user, clinic):
        return redirect("clinics:home")

    if request.method == "POST":
        form = ServiceForm(
            request.POST,
            instance=service
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Service updated successfully."
            )

            return redirect(
                "clinics:service_list",
                clinic_id=clinic.id
            )

    else:
        form = ServiceForm(instance=service)

    return render(
        request,
        "clinics/edit_service.html",
        {
            "form": form,
            "clinic": clinic,
            "service": service,
        },
    )

@login_required
def delete_service(request, clinic_id, service_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)

    service = get_object_or_404(
        Service,
        id=service_id,
        clinic=clinic
    )

    if not user_can_access_clinic(request.user, clinic):
        return redirect("clinics:home")

    if request.method == "POST":
        service.delete()

        messages.success(
            request,
            "Service deleted successfully."
        )

        return redirect(
            "clinics:service_list",
            clinic_id=clinic.id
        )

    return render(
        request,
        "clinics/delete_service.html",
        {
            "clinic": clinic,
            "service": service,
        },
    )

from django.db.models import Q

@login_required
def appointment_list(request, clinic_id):
    clinic = get_object_or_404(
        Clinic,
        id=clinic_id
    )

    if not user_can_access_clinic(request.user, clinic):
        return redirect("clinics:home")

    q = request.GET.get("q", "").strip()

    appointments = (
        clinic.appointments
        .select_related(
            "client",
            "service",
            "staff",
            "staff__user",
        )
    )

    if q:
        appointments = appointments.filter(
            Q(client__first_name__icontains=q) |
            Q(client__last_name__icontains=q) |
            Q(client__phone__icontains=q) |
            Q(service__name__icontains=q) |
            Q(staff__user__first_name__icontains=q) |
            Q(staff__user__last_name__icontains=q) |
            Q(status__icontains=q)
        )

    appointments = appointments.order_by("-appointment_datetime")

    return render(
        request,
        "clinics/appointment_list.html",
        {
            "clinic": clinic,
            "appointments": appointments,
            "search_query": q,
        },
    )

@login_required
def add_appointment(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)

    if not user_can_access_clinic(request.user, clinic):
        return redirect("clinics:home")

    if request.method == "POST":
        form = AppointmentForm(request.POST,clinic=clinic)

        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.clinic = clinic
            appointment.save()

            messages.success(
                request,
                "Appointment booked successfully."
            )

            return redirect(
                "clinics:appointment_list",
                clinic_id=clinic.id
            )

    else:
        form = AppointmentForm(clinic=clinic)

    return render(
        request,
        "clinics/add_appointment.html",
        {
            "form": form,
            "clinic": clinic,
        },
    )

@login_required
def update_appointment(
    request,
    clinic_id,
    appointment_id,
):
    clinic = get_object_or_404(
        Clinic,
        id=clinic_id
    )

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        clinic=clinic,
    )

    if not user_can_access_clinic(request.user, clinic):
        return redirect("clinics:home")

    if request.method == "POST":

        form = AppointmentForm(
            request.POST,
            instance=appointment,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Appointment updated successfully."
            )

            return redirect(
                "clinics:appointment_list",
                clinic_id=clinic.id,
            )

    else:

        form = AppointmentForm(instance=appointment)

    return render(
        request,
        "clinics/edit_appointment.html",
        {
            "form": form,
            "appointment": appointment,
            "clinic": clinic,
        },
    )

@login_required
def delete_appointment(
    request,
    clinic_id,
    appointment_id,
):
    clinic = get_object_or_404(
        Clinic,
        id=clinic_id
    )

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        clinic=clinic,
    )

    if not user_can_access_clinic(request.user, clinic):
        return redirect("clinics:home")

    if request.method == "POST":
        appointment.delete()

        messages.success(
            request,
            "Appointment deleted successfully."
        )

        return redirect(
            "clinics:appointment_list",
            clinic_id=clinic.id,
        )

    return render(
        request,
        "clinics/delete_appointment.html",
        {
            "appointment": appointment,
            "clinic": clinic,
        },
    )

from django.utils import timezone
from django.db.models import Count

@login_required
def todays_dashboard(request):

    clinic = request.user.clinics.first()  # Assuming a user can have only one clinic
    if not clinic:
        return redirect("clinics:create_clinic")  

    # clinic = get_object_or_404(
    #     Clinic,
    #     id=clinic_id
    # )

    if not user_can_access_clinic(request.user, clinic):
        return redirect("clinics:home")

    today = timezone.localdate()

    today_appointments = clinic.appointments.filter(
        appointment_datetime__date=today
    )

    context = {
        "clinic": clinic,

        "total_clients": clinic.clients.filter(is_active=True).count(),

        "total_staff": clinic.members.count(),

        "total_services": clinic.services.filter(
            is_active=True
        ).count(),

        "total_appointments": clinic.appointments.count(),

        "today_appointments_count": today_appointments.count(),

        "completed_today": today_appointments.filter(
            status="COMPLETED"
        ).count(),

        "scheduled_today": today_appointments.filter(
            status="SCHEDULED"
        ).count(),

        "cancelled_today": today_appointments.filter(
            status="CANCELLED"
        ).count(),

        "no_show_today": today_appointments.filter(
            status="NO_SHOW"
        ).count(),

        "today_appointments": today_appointments
            .select_related(
                "client",
                "service",
                "staff",
            )
            .order_by("appointment_datetime"),

        "popular_services": (
            clinic.services
            .annotate(
                total=Count("appointments")
            )
            .order_by("-total")[:5]
        ),

        "recent_clients" : clinic.clients.order_by(
            "-created_at"
        )[:5],

        "upcoming_appointments": clinic.appointments.filter(
            appointment_datetime__gte=timezone.now(),
            status="SCHEDULED"
        ).order_by("appointment_datetime")[:5],

        "recent_appointments": clinic.appointments.select_related(
            "client",
            "service",
            "staff"
        ).order_by("-created_at")[:5],

    }

    return render(
        request,
        "todays_dashboard.html",
        context,
    )

def base(request):
    return render(request,"clinics:base.html")

from django.db.models import Q
from django.http import JsonResponse


@login_required
def global_search(request):
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse({
            "clients": [],
            "staff": [],
            "services": [],
            "appointments": [],
            "knowledge": [],
        })

    clinic = request.user.clinics.first()

    if not clinic:
        return JsonResponse({"error": "Clinic not found"}, status=404)

    if not user_can_access_clinic(request.user, clinic):
        return JsonResponse({"error": "Permission denied"}, status=403)

    clients = (
        clinic.clients
        .filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query)
        )
        .values(
            "id",
            "first_name",
            "last_name",
            "phone",
        )[:5]
    )

    staff = (
        StaffMembership.objects.filter(clinic=clinic)
        .select_related("user")
        .filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query)
        )
        .values(
            "id",
            "user__first_name",
            "user__last_name",
            "user__email",
        )[:5]
    )

    services = (
        clinic.services
        .filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
        .values(
            "id",
            "name",
            "price",
        )[:5]
    )

    appointments = (
        clinic.appointments
        .select_related(
            "client",
            "service",
        )
        .filter(
            Q(client__first_name__icontains=query) |
            Q(client__last_name__icontains=query) |
            Q(service__name__icontains=query)
        )
        .values(
            "id",
            "appointment_datetime",
            "status",
            "client__first_name",
            "client__last_name",
            "service__name",
        )[:5]
    )

    knowledge = []

    # Uncomment when Knowledge Base is implemented
    #
    # knowledge = (
    #     clinic.knowledge_articles
    #     .filter(
    #         Q(title__icontains=query) |
    #         Q(content__icontains=query)
    #     )
    #     .values(
    #         "id",
    #         "title",
    #     )[:5]
    # )

    return JsonResponse({
        "clients": list(clients),
        "staff": list(staff),
        "services": list(services),
        "appointments": list(appointments),
        "knowledge": knowledge,
    })

