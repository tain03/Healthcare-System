# Healthcare System Microservices

This project is a microservices-based healthcare system that provides user management, appointment scheduling, and AI-powered chat functionality.

## Architecture

The system consists of three main microservices:

1. **Core Service** (Port 8000)
   - Handles user management
   - Manages appointments
   - Uses PostgreSQL for data storage

2. **Chat Service** (Port 8001)
   - Provides AI-powered chat functionality
   - Integrates with OpenAI's GPT-3.5
   - Uses PostgreSQL for chat history storage

3. **API Gateway** (Port 8080)
   - Single entry point for all client requests
   - Routes requests to appropriate microservices
   - Handles cross-cutting concerns

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- OpenAI API key

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
```

## Running the Services

1. Build and start all services:
```bash
docker-compose up --build
```

2. Access the services:
   - API Gateway: http://localhost:8080
   - Core Service: http://localhost:8000
   - Chat Service: http://localhost:8001

## API Documentation

Once the services are running, you can access the API documentation at:
- API Gateway: http://localhost:8080/docs
- Core Service: http://localhost:8000/docs
- Chat Service: http://localhost:8001/docs

## Features

### User Management
- Create and manage user accounts
- Different user roles (doctor, patient, admin)
- User authentication and authorization

### Appointment Management
- Schedule appointments
- View appointment history
- Update appointment status

### AI Chat
- Real-time chat with AI assistant
- Healthcare-specific responses
- Chat history storage

## Development

### Project Structure
```
healthcare_system/
├── docker-compose.yml
├── services/
│   ├── core-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── database.py
│   ├── chat-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── database.py
│   └── api-gateway/
│       ├── Dockerfile
│       ├── requirements.txt
│       └── main.py
└── README.md
```

### Adding New Features

1. Identify which service should handle the new feature
2. Add necessary models and schemas
3. Implement the feature in the service
4. Add corresponding endpoints in the API Gateway
5. Update documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
