# 🌐 Kubernetes AI Agent - Web Interface

A modern, responsive web interface for the Kubernetes AI Agent, built with Next.js and FastAPI.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI       │    │   Kubernetes    │
│   Frontend      │◄──►│   Backend       │◄──►│   Cluster       │
│   (Port 3000)   │    │   (Port 8000)   │    │   (kubectl)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ✨ Features

### 🎨 Frontend (Next.js)
- **Modern UI/UX**: Clean, responsive design with Tailwind CSS
- **Real-time Chat**: WebSocket-powered AI chat interface
- **Dashboard**: Cluster status and resource overview
- **Resource Management**: View and manage Kubernetes resources
- **Settings**: Configure AI agent and security settings
- **Dark/Light Mode**: Theme switching support
- **Mobile Responsive**: Works on all device sizes

### 🔧 Backend (FastAPI)
- **REST API**: Comprehensive API for all operations
- **WebSocket Support**: Real-time communication
- **AI Integration**: LangChain and Google Gemini integration
- **Kubernetes Operations**: Full cluster management
- **Security**: Input validation and guardrails
- **Health Checks**: Monitoring and status endpoints

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- kubectl configured for your cluster
- Google API key for Gemini

### 1. Clone the Repository
```bash
git clone https://github.com/Ragavendira1/k8sagents.git
cd k8sagents
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:
```env
GOOGLE_API_KEY=your-google-api-key-here
K8S_MODEL=gemini-2.0-flash
K8S_TEMPERATURE=0.1
K8S_MAX_TOKENS=2048
K8S_NAMESPACE=default
K8S_MAX_REPLICAS=10
```

### 3. Run with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🛠️ Development Setup

### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
npm start
```

## 📱 Web Interface Features

### 🤖 AI Chat Interface
- **Natural Language Processing**: Chat with AI using natural language
- **Real-time Communication**: WebSocket-powered instant responses
- **Quick Actions**: Pre-defined commands for common operations
- **Message History**: Persistent chat history
- **Status Indicators**: Connection and message status

### 📊 Dashboard
- **Cluster Overview**: Resource counts and status
- **Agent Status**: AI agent configuration and health
- **Quick Actions**: Common Kubernetes operations
- **Recent Activity**: Latest operations and events
- **Real-time Updates**: Live status monitoring

### 🔧 Resource Management
- **Resource Browser**: View all Kubernetes resources
- **Resource Types**: Deployments, Services, Pods, Namespaces
- **Filtering**: Search and filter resources
- **Actions**: View, edit, and delete resources
- **Real-time Refresh**: Live resource updates

### ⚙️ Settings
- **AI Configuration**: Model selection and parameters
- **Kubernetes Settings**: Namespace and resource limits
- **Security Settings**: Image whitelist and namespace restrictions
- **System Information**: Agent status and configuration

## 🔌 API Endpoints

### REST API
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/status` - Agent and cluster status
- `POST /api/chat` - Chat with AI agent
- `POST /api/deployments` - Create deployment
- `POST /api/services` - Create service
- `GET /api/resources/{type}` - List resources
- `POST /api/scale` - Scale deployment
- `POST /api/logs` - Get pod logs

### WebSocket
- `WS /ws` - Real-time communication

## 🐳 Docker Deployment

### Single Container
```bash
# Build and run backend
cd backend
docker build -t k8s-ai-backend .
docker run -p 8000:8000 -v ~/.kube:/home/app/.kube:ro k8s-ai-backend

# Build and run frontend
cd frontend
docker build -t k8s-ai-frontend .
docker run -p 3000:3000 k8s-ai-frontend
```

### Docker Compose
```bash
# Start all services
docker-compose up -d

# Scale services
docker-compose up -d --scale backend=2

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🔒 Security Features

### Input Validation
- **Sanitization**: All inputs are sanitized and validated
- **Type Checking**: Strong typing with Pydantic models
- **Length Limits**: Input length restrictions

### Kubernetes Security
- **Namespace Restrictions**: Prevent operations on system namespaces
- **Image Whitelist**: Only allow approved container images
- **Resource Limits**: Configurable resource usage limits
- **RBAC Integration**: Respects Kubernetes RBAC policies

### API Security
- **CORS Configuration**: Proper cross-origin resource sharing
- **Rate Limiting**: Request rate limiting (configurable)
- **Error Handling**: Secure error messages without sensitive data

## 📊 Monitoring and Logging

### Health Checks
- **Backend**: `/health` endpoint
- **Frontend**: Built-in health monitoring
- **Docker**: Container health checks

### Logging
- **Structured Logging**: JSON-formatted logs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Request Tracking**: Request/response logging

### Metrics
- **Resource Usage**: CPU and memory monitoring
- **Request Metrics**: API call statistics
- **Error Rates**: Error tracking and alerting

## 🚀 Production Deployment

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: k8s-ai-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: k8s-ai-agent
  template:
    metadata:
      labels:
        app: k8s-ai-agent
    spec:
      containers:
      - name: backend
        image: k8s-ai-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-agent-secrets
              key: google-api-key
      - name: frontend
        image: k8s-ai-frontend:latest
        ports:
        - containerPort: 3000
```

### Environment Variables
```env
# Production environment
NODE_ENV=production
GOOGLE_API_KEY=your-production-api-key
K8S_MODEL=gemini-2.0-flash
K8S_NAMESPACE=default
K8S_MAX_REPLICAS=50
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- **Frontend**: ESLint + Prettier
- **Backend**: Black + Flake8
- **TypeScript**: Strict mode enabled
- **Python**: Type hints required

### Testing
```bash
# Frontend tests
cd frontend
npm test
npm run lint
npm run type-check

# Backend tests
cd backend
pytest
flake8 .
black --check .
```

## 📚 Documentation

- **API Documentation**: http://localhost:8000/docs
- **Frontend Components**: See `/frontend/components/`
- **Backend Models**: See `/backend/main.py`
- **Configuration**: See environment variables

## 🆘 Troubleshooting

### Common Issues

1. **Connection Issues**
   - Check if kubectl is configured
   - Verify API key is set correctly
   - Check network connectivity

2. **Build Issues**
   - Ensure Docker is running
   - Check for port conflicts
   - Verify environment variables

3. **Permission Issues**
   - Check kubectl permissions
   - Verify namespace access
   - Check RBAC policies

### Debug Mode
```bash
# Backend debug
docker-compose logs -f backend

# Frontend debug
docker-compose logs -f frontend

# Enable verbose logging
export K8S_VERBOSE=true
docker-compose up
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org/) - React framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework
- [LangChain](https://langchain.com/) - AI framework
- [Google Gemini](https://ai.google.dev/) - AI model