# 🏥 Healthcare Management System

[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![AI Chat](https://img.shields.io/badge/AI%20Chat-Enabled-orange.svg)](LLM_INTEGRATION.md)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A comprehensive Django-based healthcare management system designed to streamline interactions between patients, doctors, and healthcare providers.

## 🔍 Overview

This Healthcare Management System is a web-based application that provides a centralized platform for managing healthcare services. It connects patients, doctors, nurses, administrators, pharmacists, lab technicians, and insurance providers through a unified interface, enabling efficient healthcare delivery and management. The system features an AI-powered chat assistant that provides instant responses to health-related questions, enhancing patient education and support.

## ✨ Features

### 👤 Multi-User Role System
- 🧑 **Patient Portal**: Book appointments, view medical records, manage prescriptions, access lab results, and pay bills
- 👨‍⚕️ **Doctor Dashboard**: Manage appointments, access patient records, prescribe treatments, and order lab tests
- 👩‍⚕️ **Nurse Interface**: View patient information and manage daily appointments
- 💻 **Administrator Panel**: Manage users and system settings
- 👨‍🔬 **Pharmacist Module**: Process and fill prescriptions
- 🧪 **Lab Technician Portal**: Process lab tests and upload results
- 💰 **Insurance Provider Interface**: Process insurance claims
- 🤖 **AI Health Assistant**: Get instant answers to health-related questions through an intelligent chat interface

### 💪 Core Functionalities

#### 🧑 For Patients
- 📅 **Appointment Management**: Book, view, and cancel appointments
- 📝 **Medical Records**: Access complete medical history
- 💊 **Prescription Management**: View active and past prescriptions
- 🔍 **Lab Results**: Access test results and status updates
- 💳 **Billing**: View and pay medical bills online

#### 👨‍⚕️ For Doctors
- 📆 **Appointment Scheduling**: View and manage daily, upcoming, and past appointments
- 💼 **Patient Management**: Access comprehensive patient information
- 📚 **Electronic Health Records**: Create and update medical records
- 💉 **E-Prescribing**: Generate digital prescriptions
- 🧪 **Lab Orders**: Request laboratory tests and view results

#### 👩‍⚕️ For Healthcare Staff
- 📂 **Patient Management**: Access and update patient information
- 📅 **Appointment Tracking**: Monitor scheduled appointments
- ✅ **Task Management**: Assign and track healthcare tasks
- 📊 **Reporting**: Generate and view healthcare reports

#### 🤖 AI Health Assistant
- 💬 **Intelligent Chat**: Engage in natural conversations about health topics
- 👨‍⚕️ **Medical Information**: Get reliable answers to common health questions
- 🔍 **Symptom Guidance**: Receive preliminary information about symptoms
- 📝 **Health Tips**: Access preventive care advice and wellness recommendations
- 🔗 **Service Connection**: Get directed to appropriate healthcare services when needed

## 🛠️ Technical Architecture

### ⚙️ Backend
- **Framework**: Django 5.2
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **Authentication**: Django's built-in authentication with custom user model
- **Authorization**: Role-based access control

### 💻 Frontend
- **UI Framework**: Bootstrap 5
- **JavaScript Libraries**: jQuery, Flatpickr (date/time picker)
- **Responsive Design**: Mobile-friendly interface

## 💾 Installation

1️⃣ Clone the repository:
   ```bash
   git clone https://github.com/tain03/healthcare-system.git
   cd healthcare-system
   ```

2️⃣ Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3️⃣ Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4️⃣ Apply migrations:
   ```bash
   python manage.py migrate
   ```

5️⃣ Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6️⃣ Run the development server:
   ```bash
   python manage.py runserver
   ```

7️⃣ Access the application at http://127.0.0.1:8000/

8️⃣ (Optional) Set up the LLM for enhanced AI chat:
   ```bash
   # Install additional dependencies for LLM support
   pip install transformers torch accelerate bitsandbytes sentencepiece

   # Run the LLM setup script
   python setup_llm.py
   ```
   See `LLM_INTEGRATION.md` for detailed configuration options.

## 📂 Project Structure

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
├── chat/                   # AI Chat application
│   ├── migrations/        # Database migrations
│   ├── templates/         # Chat templates
│   ├── services.py         # AI service integration
│   ├── models.py          # Chat models
│   ├── urls.py            # Chat URL routing
│   └── views.py           # Chat view functions
├── healthcare_system/     # Project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL routing
│   └── wsgi.py            # WSGI configuration
├── static/                # Static files (CSS, JS, images)
├── media/                 # User-uploaded files
├── manage.py              # Django management script
├── requirements.txt       # Project dependencies
├── LLM_INTEGRATION.md     # LLM integration documentation
└── README.md              # Project documentation
```

## 🔗 User Roles and Workflows

### 🧑 Patient Workflow
1. Register/Login to the system
2. Book appointments with doctors
3. View medical history and prescriptions
4. Access lab test results
5. Pay medical bills
6. Chat with AI Health Assistant for health-related questions

### 👨‍⚕️ Doctor Workflow
1. Login to the system
2. View scheduled appointments
3. Access patient medical records
4. Create prescriptions and order lab tests
5. Update patient information
6. Use AI Health Assistant for reference information

### 💻 Administrator Workflow
1. Manage user accounts
2. Configure system settings
3. Generate reports
4. Monitor system activity

## 💡 Future Enhancements

- 📹 **Telemedicine Integration**: Virtual consultations and remote patient monitoring
- 📱 **Mobile Application**: Native mobile apps for iOS and Android
- 🤖 **Advanced AI Capabilities**: Expand AI chat with medical image analysis and personalized health recommendations
- 📈 **Health Analytics**: Advanced reporting and analytics dashboard
- 🔔 **Patient Portal Enhancements**: Appointment reminders, medication alerts
- 🔗 **Integration with External Systems**: Electronic Medical Records (EMR) systems, pharmacy systems
- 🌐 **Multilingual Support**: Extend AI chat to support multiple languages

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
