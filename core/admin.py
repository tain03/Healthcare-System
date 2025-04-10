from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Patient, Doctor, Nurse, Administrator, Pharmacist,
    InsuranceProvider, LabTechnician, Appointment, MedicalRecord,
    Prescription, LabTest, Bill, InsuranceClaim
)

# Register User model with custom UserAdmin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'address', 'date_of_birth')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'address', 'date_of_birth')}),
    )

admin.site.register(User, CustomUserAdmin)

# Register Patient model
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'blood_group', 'insurance_id')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'blood_group')

# Register Doctor model
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'license_number', 'consultation_fee')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization')

# Register Nurse model
@admin.register(Nurse)
class NurseAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'license_number')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department')

# Register Administrator model
@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'employee_id')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department')

# Register Pharmacist model
@admin.register(Pharmacist)
class PharmacistAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

# Register InsuranceProvider model
@admin.register(InsuranceProvider)
class InsuranceProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'provider_id')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'company_name')

# Register LabTechnician model
@admin.register(LabTechnician)
class LabTechnicianAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'license_number')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization')

# Register Appointment model
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'doctor__user__first_name', 'doctor__user__last_name')

# Register MedicalRecord model
@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'diagnosis')
    list_filter = ('date',)
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'diagnosis')

# Register Prescription model
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'medication_name', 'status', 'date_prescribed', 'expiry_date')
    list_filter = ('status', 'date_prescribed')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'medication_name')

# Register LabTest model
@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'test_name', 'status', 'ordered_date', 'result_date')
    list_filter = ('status', 'ordered_date')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'test_name')

# Register Bill model
@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('patient', 'amount', 'status', 'due_date', 'paid_date')
    list_filter = ('status', 'due_date')
    search_fields = ('patient__user__first_name', 'patient__user__last_name')

# Register InsuranceClaim model
@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
    list_display = ('patient', 'insurance_provider', 'claim_number', 'amount_claimed', 'status')
    list_filter = ('status', 'submitted_date')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'claim_number')
