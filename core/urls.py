from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Patient URLs
    path('patient/appointments/', views.patient_appointments, name='patient_appointments'),
    path('patient/book-appointment/', views.book_appointment, name='book_appointment'),
    path('patient/medical-records/', views.patient_medical_records, name='patient_medical_records'),
    path('patient/prescriptions/', views.patient_prescriptions, name='patient_prescriptions'),
    path('patient/lab-tests/', views.patient_lab_tests, name='patient_lab_tests'),
    path('patient/bills/', views.patient_bills, name='patient_bills'),
    path('patient/pay-bill/<int:bill_id>/', views.pay_bill, name='pay_bill'),
    path('appointment/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),

    # Doctor URLs
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/patients/', views.doctor_patients, name='doctor_patients'),
    path('doctor/patient/<int:patient_id>/', views.doctor_patient_detail, name='doctor_patient_detail'),
    path('doctor/add-prescription/', views.add_prescription, name='add_prescription'),
    path('doctor/add-medical-record/', views.add_medical_record, name='add_medical_record'),
    path('doctor/order-lab-test/', views.order_lab_test, name='order_lab_test'),
    path('appointment/update-status/<int:appointment_id>/', views.update_appointment_status, name='update_appointment_status'),

    # Nurse URLs
    path('nurse/patients/', views.nurse_patients, name='nurse_patients'),
    path('nurse/appointments/', views.nurse_appointments, name='nurse_appointments'),

    # Admin URLs
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/add-user/', views.admin_add_user, name='admin_add_user'),

    # Pharmacist URLs
    path('pharmacist/prescriptions/', views.pharmacist_prescriptions, name='pharmacist_prescriptions'),
    path('pharmacist/fill-prescription/<int:prescription_id>/', views.fill_prescription, name='fill_prescription'),

    # Lab Technician URLs
    path('lab/tests/', views.lab_tests, name='lab_tests'),
    path('lab/update-test/<int:test_id>/', views.update_lab_test, name='update_lab_test'),

    # Insurance Provider URLs
    path('insurance/claims/', views.insurance_claims, name='insurance_claims'),
    path('insurance/process-claim/<int:claim_id>/', views.process_claim, name='process_claim'),
]
