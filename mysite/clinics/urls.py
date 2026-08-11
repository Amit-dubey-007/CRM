from django.urls import path
from . import views

app_name = "clinics"

urlpatterns = [
    path('home', views.home, name='home'),
    path('create/', views.create_clinic, name='create_clinic'),
    path('dashboard/', views.clinic_dashboard, name='dashboard'),
    path('<int:clinic_id>/edit/', views.edit_clinic, name='edit_clinic'),
    path('<int:clinic_id>/', views.clinic_detail, name='clinic_detail'),
    path('<int:clinic_id>/delete/', views.delete_clinic, name='delete_clinic'),
    path('<int:clinic_id>/add-staff/', views.add_staff, name='add_staff'),
    path('<int:clinic_id>/remove-staff/<int:staff_id>/', views.remove_staff, name='remove_staff'),
    path('<int:clinic_id>/update-staff/<int:staff_id>/', views.update_staff, name='update_staff'),
    path('<int:clinic_id>/staff-list/', views.staff_list, name='staff_list'),
    path('<int:clinic_id>/add-client/', views.add_client, name='add_client'),
    path('<int:clinic_id>/client-list/', views.client_list, name='client_list'),
    path('<int:clinic_id>/update-client/<int:client_id>/', views.update_client, name='update_client'),
    path('<int:clinic_id>/delete-client/<int:client_id>/', views.delete_client, name='delete_client'),

    path(
        "<int:clinic_id>/services/",
        views.service_list,
        name="service_list",
    ),

    path(
        "<int:clinic_id>/add-service/",
        views.add_service,
        name="add_service",
    ),

    path(
        "<int:clinic_id>/service/<int:service_id>/edit/",
        views.update_service,
        name="update_service",
    ),

    path(
        "<int:clinic_id>/service/<int:service_id>/delete/",
        views.delete_service,
        name="delete_service",
    ),

    path(
        "<int:clinic_id>/appointment/<int:appointment_id>/delete/",
        views.delete_appointment,
        name="delete_appointment",
    ),

    path(
        "<int:clinic_id>/appointments/",
        views.appointment_list,
        name="appointment_list",
    ),

    path(
        "<int:clinic_id>/add-appointment/",
        views.add_appointment,
        name="add_appointment",
    ),

    path(
        "<int:clinic_id>/appointment/<int:appointment_id>/edit/",
        views.update_appointment,
        name="update_appointment",
    ),

    path(
        "today-dashboard",views.todays_dashboard,name="todays_dashboard"
    ),
    path("base",views.base,name="base"),
]