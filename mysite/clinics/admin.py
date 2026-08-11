from django.contrib import admin

from .models import Clinic,StaffMembership,Appointment

# Register your models here.
admin.site.register(Clinic)
admin.site.register(StaffMembership)
admin.site.register(Appointment)