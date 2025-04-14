# 🏥 Healthcare System

A comprehensive Django-based healthcare management system with AI-powered chat functionality.

## 📋 Features

- 👩‍⚕️ User roles (Patients, Doctors, Administrators)
- 📊 Patient health records management
- 🗓️ Appointment scheduling
- 💬 Chat system for patient-doctor communication
- 🤖 AI-powered health assistant
- 📱 Responsive design for mobile and desktop

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Django 5.0+
- Other dependencies listed in requirements.txt

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/healthcare-system.git
   cd healthcare-system
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## 🤖 AI Chat Integration

The system includes an AI-powered health assistant that can answer general health questions. This feature uses a hybrid approach:

1. **Rule-based responses**: Pre-defined responses for common health questions
2. **LLM-powered responses**: For more complex or unique questions using OpenAI's models

### Chat Features

- 💬 **Patient-Doctor Chat**: Direct communication between patients and their doctors
- 🤖 **AI Health Assistant**: AI-powered chat for answering health-related questions
- ⭐ **Rating System**: Users can rate AI responses and provide feedback
- 📱 **Real-time Updates**: Messages update in real-time without page refresh
- 📊 **Unread Message Tracking**: Visual indicators for unread messages

### OpenAI Integration

The system supports integration with OpenAI's powerful language models, including the efficient gpt-4o-mini model:

1. Install the OpenAI package:
   ```bash
   pip install openai
   ```

2. Configure OpenAI:
   - The system uses environment variables for API keys
   - Make sure your `.env` file contains your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```
   - The settings.py file is already configured to use this environment variable:
     ```python
     # LLM Settings
     LLM_USE_API = True
     LLM_API_PROVIDER = 'openai'
     LLM_API_KEY = os.environ.get('OPENAI_API_KEY', '')
     LLM_MODEL_NAME = 'gpt-4o-mini'  # Efficient and powerful model
     LLM_RULE_THRESHOLD = 0.0  # Always use LLM responses
     ```

3. Run the setup script:
   ```bash
   # The script will use the API key from your environment variables
   python healthcare_system/setup_llm.py --use-api --api-provider openai --model gpt-4o-mini
   ```

4. Test the OpenAI integration:
   ```bash
   python healthcare_system/test_openai.py
   ```

5. Quick test with a direct script:
   ```bash
   python test_openai_direct.py
   ```

For more information about the LLM integration, see `healthcare_system/LLM_INTEGRATION.md`.

## 📱 Usage

1. Access the admin interface at http://localhost:8000/admin/
2. Log in with your superuser credentials
3. Create users with different roles (patients, doctors)
4. Access the main application at http://localhost:8000/

## 🔒 Security Considerations

### Protecting API Keys

This project uses environment variables to protect sensitive information like API keys:

1. **Environment Variables**: API keys are loaded from environment variables using python-dotenv
2. **Local Development**: Store your API keys in a `.env` file (not committed to Git)
3. **Before Pushing to GitHub**:
   - Make sure your `.env` file is in `.gitignore`
   - Clean up `__pycache__` directories that might contain compiled settings with API keys:
     ```bash
     python clean_pycache.py
     ```
   - Or install the pre-commit hook:
     ```bash
     # On Linux/Mac
     cp pre-commit .git/hooks/
     chmod +x .git/hooks/pre-commit

     # On Windows
     copy pre-commit .git\hooks\
     ```

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django community
- OpenAI for their powerful language models
- All contributors to this project
