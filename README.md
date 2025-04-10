# Healthcare Management System

A comprehensive Django-based healthcare management system designed to streamline interactions between patients, doctors, and healthcare providers.

## Overview

This Healthcare Management System is a web-based application that provides a centralized platform for managing healthcare services. It connects patients, doctors, nurses, administrators, pharmacists, lab technicians, and insurance providers through a unified interface, enabling efficient healthcare delivery and management.

## Features

### Multi-User Role System
- **Patient Portal**: Book appointments, view medical records, manage prescriptions, access lab results, and pay bills
- **Doctor Dashboard**: Manage appointments, access patient records, prescribe treatments, and order lab tests
- **Nurse Interface**: View patient information and manage daily appointments
- **Administrator Panel**: Manage users and system settings
- **Pharmacist Module**: Process and fill prescriptions
- **Lab Technician Portal**: Process lab tests and upload results
- **Insurance Provider Interface**: Process insurance claims

### Core Functionalities

#### For Patients
- **Appointment Management**: Book, view, and cancel appointments
- **Medical Records**: Access complete medical history
- **Prescription Management**: View active and past prescriptions
- **Lab Results**: Access test results and status updates
- **Billing**: View and pay medical bills online

#### For Doctors
- **Appointment Scheduling**: View and manage daily, upcoming, and past appointments
- **Patient Management**: Access comprehensive patient information
- **Electronic Health Records**: Create and update medical records
- **E-Prescribing**: Generate digital prescriptions
- **Lab Orders**: Request laboratory tests and view results

#### For Healthcare Staff
- **Patient Management**: Access and update patient information
- **Appointment Tracking**: Monitor scheduled appointments
- **Task Management**: Assign and track healthcare tasks
- **Reporting**: Generate and view healthcare reports

## Technical Architecture

### Backend
- **Framework**: Django 5.2
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **Authentication**: Django's built-in authentication with custom user model
- **Authorization**: Role-based access control

### Frontend
- **UI Framework**: Bootstrap 5
- **JavaScript Libraries**: jQuery, Flatpickr (date/time picker)
- **Responsive Design**: Mobile-friendly interface

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/tain03/healthcare-system.git
   cd healthcare-system
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## Project Structure

```
healthcare_system/
├── core/                  # Main application
│   ├── migrations/        # Database migrations
│   ├── templates/         # HTML templates
│   │   ├── core/          # Base templates
│   │   ├── patient/       # Patient-specific templates
│   │   ├── doctor/        # Doctor-specific templates
│   │   └── ...            # Other role-specific templates
│   ├── templatetags/      # Custom template tags and filters
│   ├── admin.py           # Admin site configuration
│   ├── models.py          # Database models
│   ├── urls.py            # URL routing
│   └── views.py           # View functions
├── healthcare_system/     # Project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL routing
│   └── wsgi.py            # WSGI configuration
├── static/                # Static files (CSS, JS, images)
├── media/                 # User-uploaded files
├── manage.py              # Django management script
└── README.md              # Project documentation
```

## User Roles and Workflows

### Patient Workflow
1. Register/Login to the system
2. Book appointments with doctors
3. View medical history and prescriptions
4. Access lab test results
5. Pay medical bills

### Doctor Workflow
1. Login to the system
2. View scheduled appointments
3. Access patient medical records
4. Create prescriptions and order lab tests
5. Update patient information

### Administrator Workflow
1. Manage user accounts
2. Configure system settings
3. Generate reports
4. Monitor system activity

## Future Enhancements

- **Telemedicine Integration**: Virtual consultations and remote patient monitoring
- **Mobile Application**: Native mobile apps for iOS and Android
- **AI Diagnostics**: Integration with AI for preliminary diagnostics
- **Health Analytics**: Advanced reporting and analytics dashboard
- **Patient Portal Enhancements**: Appointment reminders, medication alerts
- **Integration with External Systems**: Electronic Medical Records (EMR) systems, pharmacy systems

## License

This project is licensed under the MIT License - see the LICENSE file for details.
