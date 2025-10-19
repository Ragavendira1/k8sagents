# 🚀 Enhanced Kubernetes AI Agent

A powerful, intelligent Kubernetes management agent powered by LangChain and Google's Gemini AI. This agent provides a user-friendly interface for managing Kubernetes clusters with advanced features, comprehensive error handling, and security guardrails.

## ✨ Features

### 🤖 AI-Powered Operations
- **Intelligent Command Processing**: Natural language understanding for Kubernetes operations
- **Context-Aware Responses**: Maintains conversation history and context
- **Smart Error Handling**: Provides helpful error messages and recovery suggestions

### 🛡️ Security & Guardrails
- **Input Validation**: Comprehensive validation for all user inputs
- **Security Checks**: Prevents operations on forbidden namespaces
- **Resource Limits**: Configurable limits on replicas and resource usage
- **Image Whitelisting**: Control which container images can be deployed

### 🎨 Enhanced UI/UX
- **Rich Console Interface**: Beautiful, colorized output with progress indicators
- **Syntax Highlighting**: YAML content displayed with proper highlighting
- **Interactive Tables**: Clean, organized display of Kubernetes resources
- **Progress Indicators**: Visual feedback during operations

### 🔧 Comprehensive Kubernetes Operations
- **Deployments**: Create, scale, and manage deployments with health checks
- **Services**: Expose deployments with various service types
- **Resource Management**: List, describe, and monitor cluster resources
- **Logging**: Retrieve and display pod logs
- **Configuration**: Manage ConfigMaps and Secrets

### 🏗️ Advanced Architecture
- **Modular Design**: Clean separation of concerns
- **Exception Handling**: Comprehensive error handling with specific error types
- **Logging**: Detailed logging for debugging and monitoring
- **Configuration Management**: Environment-based configuration
- **Memory Management**: Conversation memory for context retention

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- kubectl installed and configured
- Google API key for Gemini

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd k8sagents
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   export GOOGLE_API_KEY="your-google-api-key"
   export K8S_NAMESPACE="default"  # Optional
   export K8S_MAX_REPLICAS="10"    # Optional
   ```

4. **Run the agent**:
   ```bash
   python k8s.py
   ```

### Command Line Options

```bash
python k8s.py [OPTIONS]

Options:
  --config PATH        Path to configuration file
  --namespace TEXT     Default namespace to use
  --dry-run           Run in dry-run mode
  --verbose, -v       Enable verbose logging
  --help              Show help message
```

## 📖 Usage Examples

### Basic Operations

```bash
# Create a deployment
"Create a deployment named 'webapp' with nginx image and 3 replicas"

# Scale a deployment
"Scale the 'webapp' deployment to 5 replicas"

# Create a service
"Create a service for the 'webapp' deployment on port 80"

# List resources
"List all pods in the default namespace"

# Get logs
"Get logs from pod 'webapp-xxx'"
```

### Advanced Operations

```bash
# Create deployment with custom configuration
"Create a deployment called 'api' using 'node:18' image with 2 replicas, 
CPU limit 1 core, memory limit 1Gi, and environment variables"

# Create service with specific type
"Create a LoadBalancer service for 'api' on port 3000"

# Scale with validation
"Scale the 'api' deployment to 10 replicas"
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google API key for Gemini | Required |
| `K8S_MODEL` | Gemini model to use | `gemini-2.0-flash` |
| `K8S_TEMPERATURE` | LLM temperature | `0.1` |
| `K8S_MAX_TOKENS` | Maximum tokens | `2048` |
| `K8S_NAMESPACE` | Default namespace | `default` |
| `K8S_MAX_REPLICAS` | Maximum replicas allowed | `10` |

### Security Configuration

The agent includes several security features:

- **Allowed Images**: Only specific container images can be deployed
- **Forbidden Namespaces**: Prevents operations on system namespaces
- **Resource Limits**: Configurable limits on resource usage
- **Input Validation**: Comprehensive validation of all inputs

## 🏗️ Architecture

### Core Components

1. **K8sAgent**: Main agent class that orchestrates all operations
2. **K8sOperations**: Handles all Kubernetes API operations
3. **InputValidator**: Validates and sanitizes user inputs
4. **K8sUI**: Provides enhanced user interface
5. **LangChain Tools**: Individual tools for specific operations

### Error Handling

The agent includes comprehensive error handling:

- **ValidationError**: Input validation failures
- **SecurityError**: Security policy violations
- **ResourceError**: Kubernetes API operation failures
- **TimeoutError**: Operation timeouts

### Logging

Detailed logging is available at multiple levels:

- **INFO**: General operation information
- **WARNING**: Non-critical issues
- **ERROR**: Operation failures
- **DEBUG**: Detailed debugging information

## 🛠️ Development

### Project Structure

```
k8sagents/
├── k8s.py              # Main application file
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .env.example       # Environment variables example
```

### Adding New Tools

To add new Kubernetes operations:

1. Create a new tool class inheriting from `BaseTool`
2. Implement the `_run` method with proper error handling
3. Add the tool to the `K8sAgent._create_tools()` method
4. Update the agent prompt with the new tool description

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=k8s

# Run specific test
pytest test_k8s_operations.py
```

## 🔒 Security Considerations

- **API Key Management**: Store API keys securely using environment variables
- **Namespace Restrictions**: Configure forbidden namespaces appropriately
- **Image Validation**: Maintain a whitelist of allowed container images
- **Resource Limits**: Set appropriate limits to prevent resource exhaustion
- **Access Control**: Ensure proper RBAC permissions for kubectl

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the documentation
2. Review the error logs
3. Open an issue on GitHub
4. Contact the development team

## 🚀 Roadmap

- [ ] Web UI interface
- [ ] Multi-cluster support
- [ ] Custom resource definitions (CRDs)
- [ ] Helm chart management
- [ ] Monitoring and alerting integration
- [ ] Backup and restore operations
- [ ] Advanced security policies
- [ ] Performance optimization tools

---

**Happy Kubernetes Management! 🎉**