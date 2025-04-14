from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Sum
from .models import (
    User, Patient, Doctor, Nurse, Administrator, Pharmacist,
    InsuranceProvider, LabTechnician, Appointment, MedicalRecord,
    Prescription, LabTest, Bill, InsuranceClaim
)

# Home view
def home(request):
    return render(request, 'core/home.html')

# User Registration
def register(request):
    if request.method == 'POST':
        # Process registration form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        date_of_birth = request.POST.get('date_of_birth')

        # Validate form data
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('core:register')

        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type,
                phone_number=phone_number,
                address=address,
                date_of_birth=date_of_birth if date_of_birth else None
            )

            # Create specific user profile based on user_type
            if user_type == 'patient':
                Patient.objects.create(user=user)
            elif user_type == 'doctor':
                Doctor.objects.create(
                    user=user,
                    specialization='General',  # Default value, can be updated later
                    license_number='TBD'  # Default value, can be updated later
                )
            # Add other user types as needed

            messages.success(request, 'Registration successful. Please log in.')
            return redirect('core:login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect('core:register')

    return render(request, 'core/register.html')

# User Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'core/login.html')

# User Logout
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('core:home')

# Dashboard view - redirects to appropriate dashboard based on user type
@login_required
def dashboard(request):
    user_type = request.user.user_type

    if user_type == 'patient':
        return render(request, 'core/patient/dashboard.html')
    elif user_type == 'doctor':
        return render(request, 'core/doctor/dashboard.html')
    elif user_type == 'nurse':
        return render(request, 'core/nurse/dashboard.html')
    elif user_type == 'admin':
        return render(request, 'core/admin/dashboard.html')
    elif user_type == 'pharmacist':
        return render(request, 'core/pharmacist/dashboard.html')
    elif user_type == 'insurance':
        return render(request, 'core/insurance/dashboard.html')
    elif user_type == 'lab_tech':
        return render(request, 'core/lab_tech/dashboard.html')
    else:
        messages.error(request, 'Invalid user type')
        return redirect('core:home')

# Patient Views
@login_required
def patient_appointments(request):
    if request.user.user_type != 'patient':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    patient = Patient.objects.get(user=request.user)
    appointments = Appointment.objects.filter(patient=patient).order_by('-date', '-time')

    return render(request, 'core/patient/appointments.html', {'appointments': appointments})

@login_required
def book_appointment(request):
    if request.user.user_type != 'patient':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        date = request.POST.get('date')
        time = request.POST.get('time')
        reason = request.POST.get('reason')

        patient = Patient.objects.get(user=request.user)
        doctor = Doctor.objects.get(id=doctor_id)

        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=date,
            time=time,
            reason=reason,
            status='scheduled'
        )

        messages.success(request, 'Appointment booked successfully')
        return redirect('core:patient_appointments')

    doctors = Doctor.objects.all()
    today = timezone.now().date()
    return render(request, 'core/patient/book_appointment.html', {'doctors': doctors, 'today': today})

@login_required
def patient_medical_records(request):
    if request.user.user_type != 'patient':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    patient = Patient.objects.get(user=request.user)
    medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-date')

    return render(request, 'core/patient/medical_records.html', {'medical_records': medical_records})

@login_required
def patient_prescriptions(request):
    if request.user.user_type != 'patient':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    patient = Patient.objects.get(user=request.user)
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-date_prescribed')

    return render(request, 'core/patient/prescriptions.html', {'prescriptions': prescriptions})

@login_required
def patient_lab_tests(request):
    if request.user.user_type != 'patient':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    patient = Patient.objects.get(user=request.user)
    lab_tests = LabTest.objects.filter(patient=patient).order_by('-ordered_date')

    return render(request, 'core/patient/lab_tests.html', {'lab_tests': lab_tests})

@login_required
def patient_bills(request):
    if request.user.user_type != 'patient':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    patient = Patient.objects.get(user=request.user)
    bills = Bill.objects.filter(patient=patient).order_by('-due_date')

    return render(request, 'core/patient/bills.html', {'bills': bills})

@login_required
def pay_bill(request, bill_id):
    if request.user.user_type != 'patient':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    bill = get_object_or_404(Bill, id=bill_id)

    if bill.patient.user != request.user:
        messages.error(request, 'Access denied')
        return redirect('core:patient_bills')

    if request.method == 'POST':
        # Process payment (in a real system, this would integrate with a payment gateway)
        bill.status = 'paid'
        bill.paid_date = timezone.now().date()
        bill.save()

        messages.success(request, 'Payment successful')
        return redirect('core:patient_bills')

    return render(request, 'core/patient/pay_bill.html', {'bill': bill})

# Doctor Views
@login_required
def doctor_appointments(request):
    if request.user.user_type != 'doctor':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    doctor = Doctor.objects.get(user=request.user)
    today = timezone.now().date()

    # Get today's appointments
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        date=today
    ).order_by('time')

    # Get upcoming appointments (future dates)
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        date__gt=today,
        status='scheduled'
    ).order_by('date', 'time')

    # Get past appointments
    past_appointments = Appointment.objects.filter(
        doctor=doctor,
        date__lt=today
    ).order_by('-date', '-time')

    # Add past appointments from today that are completed, cancelled, or no-show
    past_appointments = past_appointments | Appointment.objects.filter(
        doctor=doctor,
        date=today,
        status__in=['completed', 'cancelled', 'no_show']
    ).order_by('-date', '-time')

    context = {
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments
    }

    return render(request, 'core/doctor/appointments.html', context)

@login_required
def doctor_patients(request):
    if request.user.user_type != 'doctor':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    doctor = Doctor.objects.get(user=request.user)
    # Get unique patients who have appointments with this doctor
    patients = Patient.objects.filter(appointments__doctor=doctor).distinct()

    return render(request, 'core/doctor/patients.html', {'patients': patients})

@login_required
def doctor_patient_detail(request, patient_id):
    if request.user.user_type != 'doctor':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    doctor = Doctor.objects.get(user=request.user)
    patient = get_object_or_404(Patient, id=patient_id)

    # Check if this doctor has appointments with this patient
    if not Appointment.objects.filter(doctor=doctor, patient=patient).exists():
        messages.error(request, 'Access denied')
        return redirect('core:doctor_patients')

    medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-date')
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-date_prescribed')
    lab_tests = LabTest.objects.filter(patient=patient).order_by('-ordered_date')
    appointments = Appointment.objects.filter(doctor=doctor, patient=patient).order_by('-date', '-time')

    context = {
        'patient': patient,
        'medical_records': medical_records,
        'prescriptions': prescriptions,
        'lab_tests': lab_tests,
        'appointments': appointments
    }

    return render(request, 'core/doctor/patient_detail.html', context)

@login_required
def add_prescription(request):
    if request.user.user_type != 'doctor':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    doctor = Doctor.objects.get(user=request.user)
    selected_patient = None

    # Check if a patient was selected from another page
    patient_id = request.GET.get('patient')
    if patient_id:
        try:
            selected_patient = Patient.objects.get(id=patient_id)
            # Verify this doctor has access to this patient
            if not Appointment.objects.filter(doctor=doctor, patient=selected_patient).exists():
                messages.error(request, 'Access denied')
                return redirect('core:doctor_patients')
        except Patient.DoesNotExist:
            pass

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        medication_name = request.POST.get('medication_name')
        dosage = request.POST.get('dosage')
        frequency = request.POST.get('frequency')
        duration = request.POST.get('duration')
        notes = request.POST.get('notes')
        expiry_date = request.POST.get('expiry_date')

        patient = Patient.objects.get(id=patient_id)

        Prescription.objects.create(
            patient=patient,
            doctor=doctor,
            medication_name=medication_name,
            dosage=dosage,
            frequency=frequency,
            duration=duration,
            notes=notes,
            expiry_date=expiry_date,
            status='active'
        )

        messages.success(request, 'Prescription added successfully')
        return redirect('core:doctor_patient_detail', patient_id=patient_id)

    # Get patients who have appointments with this doctor
    patients = Patient.objects.filter(appointments__doctor=doctor).distinct()

    context = {
        'patients': patients,
        'selected_patient': selected_patient
    }

    return render(request, 'core/doctor/add_prescription.html', context)

@login_required
def add_medical_record(request):
    if request.user.user_type != 'doctor':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    doctor = Doctor.objects.get(user=request.user)
    selected_patient = None

    # Check if a patient was selected from another page
    patient_id = request.GET.get('patient')
    if patient_id:
        try:
            selected_patient = Patient.objects.get(id=patient_id)
            # Verify this doctor has access to this patient
            if not Appointment.objects.filter(doctor=doctor, patient=selected_patient).exists():
                messages.error(request, 'Access denied')
                return redirect('core:doctor_patients')
        except Patient.DoesNotExist:
            pass

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        diagnosis = request.POST.get('diagnosis')
        treatment = request.POST.get('treatment')
        notes = request.POST.get('notes')
        date = request.POST.get('date')

        patient = Patient.objects.get(id=patient_id)

        MedicalRecord.objects.create(
            patient=patient,
            doctor=doctor,
            date=date,
            diagnosis=diagnosis,
            treatment=treatment,
            notes=notes
        )

        messages.success(request, 'Medical record added successfully')
        return redirect('core:doctor_patient_detail', patient_id=patient_id)

    # Get patients who have appointments with this doctor
    patients = Patient.objects.filter(appointments__doctor=doctor).distinct()

    context = {
        'patients': patients,
        'selected_patient': selected_patient
    }

    return render(request, 'core/doctor/add_medical_record.html', context)

@login_required
def order_lab_test(request):
    if request.user.user_type != 'doctor':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    doctor = Doctor.objects.get(user=request.user)
    selected_patient = None

    # Check if a patient was selected from another page
    patient_id = request.GET.get('patient')
    if patient_id:
        try:
            selected_patient = Patient.objects.get(id=patient_id)
            # Verify this doctor has access to this patient
            if not Appointment.objects.filter(doctor=doctor, patient=selected_patient).exists():
                messages.error(request, 'Access denied')
                return redirect('core:doctor_patients')
        except Patient.DoesNotExist:
            pass

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        test_name = request.POST.get('test_name')
        description = request.POST.get('description')

        patient = Patient.objects.get(id=patient_id)

        LabTest.objects.create(
            patient=patient,
            doctor=doctor,
            test_name=test_name,
            description=description,
            status='ordered'
        )

        messages.success(request, 'Lab test ordered successfully')
        return redirect('core:doctor_patient_detail', patient_id=patient_id)

    # Get patients who have appointments with this doctor
    patients = Patient.objects.filter(appointments__doctor=doctor).distinct()

    context = {
        'patients': patients,
        'selected_patient': selected_patient
    }

    return render(request, 'core/doctor/order_lab_test.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    if request.user.user_type not in ['patient', 'doctor']:
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Check if the user has permission to cancel this appointment
    if request.user.user_type == 'patient':
        if appointment.patient.user != request.user:
            messages.error(request, 'Access denied')
            return redirect('core:patient_appointments')
    elif request.user.user_type == 'doctor':
        if appointment.doctor.user != request.user:
            messages.error(request, 'Access denied')
            return redirect('core:doctor_appointments')

    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()

        messages.success(request, 'Appointment cancelled successfully')

        if request.user.user_type == 'patient':
            return redirect('core:patient_appointments')
        else:  # doctor
            return redirect('core:doctor_appointments')

    return redirect('core:dashboard')

@login_required
def update_appointment_status(request, appointment_id):
    if request.user.user_type != 'doctor':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    doctor = Doctor.objects.get(user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Check if this doctor has permission to update this appointment
    if appointment.doctor != doctor:
        messages.error(request, 'Access denied')
        return redirect('core:doctor_appointments')

    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        if status in ['completed', 'cancelled', 'no_show']:
            appointment.status = status
            appointment.notes = notes
            appointment.save()

            messages.success(request, f'Appointment marked as {appointment.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')

        return redirect('core:doctor_appointments')

    return redirect('core:dashboard')

# Nurse Views
@login_required
def nurse_patients(request):
    if request.user.user_type != 'nurse':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    nurse = Nurse.objects.get(user=request.user)

    # Get all patients
    patients = Patient.objects.all()

    # Filter by name if provided
    name_filter = request.GET.get('name')
    if name_filter:
        patients = patients.filter(
            Q(user__first_name__icontains=name_filter) |
            Q(user__last_name__icontains=name_filter)
        )

    # Filter by blood group if provided
    blood_group_filter = request.GET.get('blood_group')
    if blood_group_filter:
        patients = patients.filter(blood_group=blood_group_filter)

    return render(request, 'core/nurse/patients.html', {
        'patients': patients,
        'name_filter': name_filter,
        'blood_group_filter': blood_group_filter,
        'nurse': nurse
    })

@login_required
def nurse_appointments(request):
    if request.user.user_type != 'nurse':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    nurse = Nurse.objects.get(user=request.user)

    # Get date from query parameters or use today
    date_str = request.GET.get('date')
    if date_str:
        try:
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date = timezone.now().date()
    else:
        date = timezone.now().date()

    # Get appointments for the selected date
    appointments = Appointment.objects.filter(date=date).order_by('time')

    # Filter by doctor if provided
    doctor_filter = request.GET.get('doctor')
    if doctor_filter:
        appointments = appointments.filter(doctor__id=doctor_filter)

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        appointments = appointments.filter(status=status_filter)

    # Get all doctors for the filter dropdown
    doctors = Doctor.objects.all()

    return render(request, 'core/nurse/appointments.html', {
        'appointments': appointments,
        'date': date,
        'doctor_filter': doctor_filter,
        'status_filter': status_filter,
        'doctors': doctors,
        'nurse': nurse
    })

@login_required
def nurse_dashboard(request):
    """Dashboard view for nurses."""
    if request.user.user_type != 'nurse':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    nurse = Nurse.objects.get(user=request.user)
    today = timezone.now().date()

    # Get today's appointments
    today_appointments = Appointment.objects.filter(date=today).order_by('time')

    # Get counts for different appointment statuses
    scheduled_count = today_appointments.filter(status='scheduled').count()
    completed_count = today_appointments.filter(status='completed').count()
    cancelled_count = today_appointments.filter(status='cancelled').count()
    no_show_count = today_appointments.filter(status='no_show').count()

    # Get total patient count
    patient_count = Patient.objects.count()

    context = {
        'today_appointments': today_appointments,
        'scheduled_count': scheduled_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'no_show_count': no_show_count,
        'patient_count': patient_count,
        'nurse': nurse,
        'today': today
    }

    return render(request, 'core/nurse/dashboard.html', context)

@login_required
def update_patient_vitals(request, patient_id):
    """Update patient vitals (blood pressure, temperature, etc.)."""
    if request.user.user_type != 'nurse':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    nurse = Nurse.objects.get(user=request.user)
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        # In a real application, you would have a model for vitals
        # For now, we'll just show a success message
        messages.success(request, f'Vitals updated for {patient.user.get_full_name()}')
        return redirect('core:nurse_patients')

    return render(request, 'core/nurse/update_vitals.html', {
        'patient': patient,
        'nurse': nurse
    })

# Admin Views
@login_required
def admin_users(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    users = User.objects.all().order_by('user_type', 'username')

    return render(request, 'core/admin/users.html', {'users': users})

@login_required
def admin_add_user(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    if request.method == 'POST':
        # Process form data similar to register view
        # But with admin privileges to create any user type
        pass

    return render(request, 'core/admin/add_user.html')

@login_required
def admin_toggle_user_status(request):
    """Toggle a user's active status (activate/deactivate)."""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')

        if not user_id or not action:
            messages.error(request, 'Invalid request')
            return redirect('core:admin_users')

        try:
            user = User.objects.get(id=user_id)

            # Don't allow deactivating yourself
            if user == request.user:
                messages.error(request, 'You cannot change your own status')
                return redirect('core:admin_users')

            if action == 'activate':
                user.is_active = True
                user.save()
                messages.success(request, f'User {user.get_full_name()} has been activated')
            elif action == 'deactivate':
                user.is_active = False
                user.save()
                messages.success(request, f'User {user.get_full_name()} has been deactivated')
            else:
                messages.error(request, 'Invalid action')
        except User.DoesNotExist:
            messages.error(request, 'User not found')

    return redirect('core:admin_users')

# Pharmacist Views
@login_required
def pharmacist_prescriptions(request):
    if request.user.user_type != 'pharmacist':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    pharmacist = Pharmacist.objects.get(user=request.user)

    # Get all prescriptions
    prescriptions = Prescription.objects.all().order_by('-date_prescribed')

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        prescriptions = prescriptions.filter(status=status_filter)
    else:
        # Default to active prescriptions if no filter is provided
        prescriptions = prescriptions.filter(status='active')

    # Filter by patient name if provided
    patient_filter = request.GET.get('patient')
    if patient_filter:
        prescriptions = prescriptions.filter(
            Q(patient__user__first_name__icontains=patient_filter) |
            Q(patient__user__last_name__icontains=patient_filter)
        )

    # Filter by medication name if provided
    medication_filter = request.GET.get('medication')
    if medication_filter:
        prescriptions = prescriptions.filter(medication_name__icontains=medication_filter)

    return render(request, 'core/pharmacist/prescriptions.html', {
        'prescriptions': prescriptions,
        'status_filter': status_filter,
        'patient_filter': patient_filter,
        'medication_filter': medication_filter,
        'pharmacist': pharmacist
    })

@login_required
def fill_prescription(request, prescription_id):
    if request.user.user_type != 'pharmacist':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    pharmacist = Pharmacist.objects.get(user=request.user)
    prescription = get_object_or_404(Prescription, id=prescription_id)

    if request.method == 'POST':
        pharmacist_notes = request.POST.get('pharmacist_notes', '')
        confirm_fill = request.POST.get('confirm_fill')

        if confirm_fill:
            # Update prescription status
            prescription.status = 'filled'
            prescription.filled_date = timezone.now().date()

            # Add pharmacist notes if provided
            if pharmacist_notes:
                if prescription.notes:
                    prescription.notes += f"\n\nPharmacist Notes [{timezone.now().date()}]:\n{pharmacist_notes}"
                else:
                    prescription.notes = f"Pharmacist Notes [{timezone.now().date()}]:\n{pharmacist_notes}"

            prescription.save()

            # Notify the patient and doctor about the filled prescription
            try:
                # This would be replaced with actual notification logic
                print(f"Notification: Prescription for {prescription.medication_name} has been filled for {prescription.patient}.")
                print(f"Notification to Dr. {prescription.doctor}: Prescription for {prescription.medication_name} has been filled for {prescription.patient}.")
            except Exception as e:
                print(f"Failed to send notification: {str(e)}")

            messages.success(request, f'Prescription for {prescription.medication_name} filled successfully')
            return redirect('core:pharmacist_prescriptions')
        else:
            messages.error(request, 'You must confirm that you have verified the prescription before filling it.')

    return render(request, 'core/pharmacist/fill_prescription.html', {
        'prescription': prescription,
        'pharmacist': pharmacist
    })

@login_required
def pharmacist_dashboard(request):
    """Dashboard view for pharmacists."""
    if request.user.user_type != 'pharmacist':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    pharmacist = Pharmacist.objects.get(user=request.user)

    # Get counts for different prescription statuses
    active_count = Prescription.objects.filter(status='active').count()
    filled_count = Prescription.objects.filter(status='filled').count()
    expired_count = Prescription.objects.filter(status='expired').count()

    # Get prescriptions filled today
    today = timezone.now().date()
    filled_today = Prescription.objects.filter(status='filled', filled_date=today).count()

    # Get recent prescriptions
    recent_prescriptions = Prescription.objects.filter(
        status='active'
    ).order_by('-date_prescribed')[:5]

    context = {
        'active_count': active_count,
        'filled_count': filled_count,
        'expired_count': expired_count,
        'filled_today': filled_today,
        'recent_prescriptions': recent_prescriptions,
        'pharmacist': pharmacist
    }

    return render(request, 'core/pharmacist/dashboard.html', context)

# Lab Technician Views
@login_required
def lab_tests(request):
    if request.user.user_type != 'lab_tech':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    lab_tech = LabTechnician.objects.get(user=request.user)

    # Get all lab tests, including completed ones
    lab_tests = LabTest.objects.all().order_by('-ordered_date')

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        lab_tests = lab_tests.filter(status=status_filter)

    # Filter by patient name if provided
    patient_filter = request.GET.get('patient')
    if patient_filter:
        lab_tests = lab_tests.filter(
            Q(patient__user__first_name__icontains=patient_filter) |
            Q(patient__user__last_name__icontains=patient_filter)
        )

    # Filter by test name if provided
    test_filter = request.GET.get('test_name')
    if test_filter:
        lab_tests = lab_tests.filter(test_name__icontains=test_filter)

    return render(request, 'core/lab_tech/lab_tests.html', {
        'lab_tests': lab_tests,
        'status_filter': status_filter,
        'patient_filter': patient_filter,
        'test_filter': test_filter
    })

@login_required
def update_lab_test(request, test_id):
    if request.user.user_type != 'lab_tech':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    lab_tech = LabTechnician.objects.get(user=request.user)
    lab_test = get_object_or_404(LabTest, id=test_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        result = request.POST.get('result')
        result_date = request.POST.get('result_date')
        notes = request.POST.get('notes', '')

        lab_test.status = status

        # Update lab test based on status
        if status == 'sample_collected':
            lab_test.lab_technician = lab_tech
            lab_test.notes = notes
        elif status == 'in_progress':
            lab_test.lab_technician = lab_tech
            lab_test.notes = notes
        elif status == 'completed':
            lab_test.result = result
            lab_test.lab_technician = lab_tech

            # Use provided result date or today
            if result_date:
                lab_test.result_date = result_date
            else:
                lab_test.result_date = timezone.now().date()

            lab_test.notes = notes

            # Notify the doctor who ordered the test
            try:
                # This would be replaced with actual notification logic
                # For now, we'll just print to console
                print(f"Notification: Lab test {lab_test.test_name} for {lab_test.patient} is completed.")
            except Exception as e:
                print(f"Failed to send notification: {str(e)}")
        elif status == 'cancelled':
            lab_test.notes = notes

        lab_test.save()

        messages.success(request, 'Lab test updated successfully')
        return redirect('core:lab_tests')

    return render(request, 'core/lab_tech/update_lab_test.html', {'lab_test': lab_test})

@login_required
def lab_tech_dashboard(request):
    """Dashboard view for lab technicians."""
    if request.user.user_type != 'lab_tech':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    lab_tech = LabTechnician.objects.get(user=request.user)

    # Get counts for different test statuses
    ordered_count = LabTest.objects.filter(status='ordered').count()
    in_progress_count = LabTest.objects.filter(status='in_progress').count()
    completed_count = LabTest.objects.filter(status='completed', lab_technician=lab_tech).count()

    # Get recent tests assigned to this lab technician
    recent_tests = LabTest.objects.filter(
        Q(status='ordered') | Q(status='in_progress') | Q(lab_technician=lab_tech)
    ).order_by('-ordered_date')[:5]

    # Get tests completed today
    today = timezone.now().date()
    completed_today = LabTest.objects.filter(result_date=today, lab_technician=lab_tech).count()

    context = {
        'ordered_count': ordered_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'recent_tests': recent_tests,
        'completed_today': completed_today,
        'lab_tech': lab_tech
    }

    return render(request, 'core/lab_tech/dashboard.html', context)

# Insurance Provider Views
@login_required
def insurance_claims(request):
    if request.user.user_type != 'insurance':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    insurance_provider = InsuranceProvider.objects.get(user=request.user)

    # Get all claims for this insurance provider
    claims = InsuranceClaim.objects.filter(insurance_provider=insurance_provider).order_by('-submitted_date')

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        claims = claims.filter(status=status_filter)

    # Filter by patient name if provided
    patient_filter = request.GET.get('patient')
    if patient_filter:
        claims = claims.filter(
            Q(patient__user__first_name__icontains=patient_filter) |
            Q(patient__user__last_name__icontains=patient_filter)
        )

    # Filter by claim number if provided
    claim_filter = request.GET.get('claim_number')
    if claim_filter:
        claims = claims.filter(claim_number__icontains=claim_filter)

    return render(request, 'core/insurance/claims.html', {
        'claims': claims,
        'status_filter': status_filter,
        'patient_filter': patient_filter,
        'claim_filter': claim_filter
    })

@login_required
def process_claim(request, claim_id):
    if request.user.user_type != 'insurance':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    insurance_provider = InsuranceProvider.objects.get(user=request.user)
    claim = get_object_or_404(InsuranceClaim, id=claim_id, insurance_provider=insurance_provider)

    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        claim.status = status
        claim.notes = notes
        claim.processed_date = timezone.now().date()
        claim.save()

        # If claim is approved, update the bill's insurance coverage
        if status == 'approved':
            bill = claim.bill
            bill.insurance_coverage = claim.amount_claimed

            # If insurance covers the full amount, mark bill as paid
            if bill.insurance_coverage >= bill.amount:
                bill.status = 'paid'
                bill.paid_date = timezone.now().date()
            else:
                # Calculate remaining amount
                remaining = bill.amount - bill.insurance_coverage
                # Update bill description to reflect insurance payment
                bill.description += f"\n[{timezone.now().date()}] Insurance payment of ${bill.insurance_coverage} processed. Remaining balance: ${remaining}"

            bill.save()

            # Notify the patient about the approved claim
            try:
                # This would be replaced with actual notification logic
                # For now, we'll just print to console
                print(f"Notification: Claim #{claim.claim_number} for {claim.patient} has been approved.")
            except Exception as e:
                print(f"Failed to send notification: {str(e)}")

        elif status == 'denied':
            # Notify the patient about the denied claim
            try:
                # This would be replaced with actual notification logic
                print(f"Notification: Claim #{claim.claim_number} for {claim.patient} has been denied.")
            except Exception as e:
                print(f"Failed to send notification: {str(e)}")

        messages.success(request, f'Claim {claim.claim_number} has been {claim.get_status_display().lower()} successfully')
        return redirect('core:insurance_claims')

    return render(request, 'core/insurance/process_claim.html', {'claim': claim})

@login_required
def insurance_dashboard(request):
    """Dashboard view for insurance providers."""
    if request.user.user_type != 'insurance':
        messages.error(request, 'Access denied')
        return redirect('core:dashboard')

    insurance_provider = InsuranceProvider.objects.get(user=request.user)

    # Get counts for different claim statuses
    submitted_count = InsuranceClaim.objects.filter(insurance_provider=insurance_provider, status='submitted').count()
    in_review_count = InsuranceClaim.objects.filter(insurance_provider=insurance_provider, status='in_review').count()
    approved_count = InsuranceClaim.objects.filter(insurance_provider=insurance_provider, status='approved').count()
    denied_count = InsuranceClaim.objects.filter(insurance_provider=insurance_provider, status='denied').count()

    # Get total amount of approved claims
    total_approved = InsuranceClaim.objects.filter(
        insurance_provider=insurance_provider,
        status='approved'
    ).aggregate(total=Sum('amount_claimed'))['total'] or 0

    # Get recent claims
    recent_claims = InsuranceClaim.objects.filter(
        insurance_provider=insurance_provider
    ).order_by('-submitted_date')[:5]

    # Get claims processed today
    today = timezone.now().date()
    processed_today = InsuranceClaim.objects.filter(
        insurance_provider=insurance_provider,
        processed_date=today
    ).count()

    context = {
        'submitted_count': submitted_count,
        'in_review_count': in_review_count,
        'approved_count': approved_count,
        'denied_count': denied_count,
        'total_approved': total_approved,
        'recent_claims': recent_claims,
        'processed_today': processed_today,
        'insurance_provider': insurance_provider
    }

    return render(request, 'core/insurance/dashboard.html', context)
