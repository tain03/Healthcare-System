from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Custom User Model
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('admin', 'Administrator'),
        ('pharmacist', 'Pharmacist'),
        ('insurance', 'Insurance Provider'),
        ('lab_tech', 'Lab Technician'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"

# Patient Model
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=15, blank=True, null=True)
    insurance_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"

# Doctor Model
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_days = models.CharField(max_length=100, blank=True, null=True)  # e.g., "Mon,Tue,Wed"
    available_hours = models.CharField(max_length=100, blank=True, null=True)  # e.g., "09:00-17:00"

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} ({self.specialization})"

# Nurse Model
class Nurse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nurse_profile')
    department = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)

    def __str__(self):
        return f"Nurse: {self.user.get_full_name()} ({self.department})"

# Administrator Model
class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    department = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50)

    def __str__(self):
        return f"Admin: {self.user.get_full_name()} ({self.department})"

# Pharmacist Model
class Pharmacist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pharmacist_profile')
    license_number = models.CharField(max_length=50)

    def __str__(self):
        return f"Pharmacist: {self.user.get_full_name()}"

# Insurance Provider Model
class InsuranceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='insurance_profile')
    company_name = models.CharField(max_length=100)
    provider_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.company_name} ({self.user.get_full_name()})"

# Lab Technician Model
class LabTechnician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lab_tech_profile')
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)

    def __str__(self):
        return f"Lab Tech: {self.user.get_full_name()} ({self.specialization})"

# Appointment Model
class Appointment(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.date} at {self.time}"

# Medical Record Model
class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='medical_records')
    date = models.DateField()
    diagnosis = models.TextField()
    treatment = models.TextField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Medical Record for {self.patient} on {self.date}"

# Prescription Model
class Prescription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('filled', 'Filled'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    medication_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    date_prescribed = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()

    def __str__(self):
        return f"{self.medication_name} for {self.patient}"

# Lab Test Model
class LabTest(models.Model):
    STATUS_CHOICES = (
        ('ordered', 'Ordered'),
        ('sample_collected', 'Sample Collected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_tests')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='ordered_lab_tests')
    test_name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    ordered_date = models.DateField(auto_now_add=True)
    result = models.TextField(blank=True, null=True)
    result_date = models.DateField(blank=True, null=True)
    lab_technician = models.ForeignKey(LabTechnician, on_delete=models.SET_NULL, null=True, blank=True, related_name='conducted_tests')

    def __str__(self):
        return f"{self.test_name} for {self.patient}"

# Bill Model
class Bill(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bills')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    paid_date = models.DateField(blank=True, null=True)
    insurance_coverage = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Bill #{self.id} for {self.patient} - ${self.amount}"

# Insurance Claim Model
class InsuranceClaim(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('paid', 'Paid'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurance_claims')
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='insurance_claims')
    insurance_provider = models.ForeignKey(InsuranceProvider, on_delete=models.CASCADE, related_name='claims')
    claim_number = models.CharField(max_length=50)
    amount_claimed = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    submitted_date = models.DateField(auto_now_add=True)
    processed_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Claim #{self.claim_number} for {self.patient}"
