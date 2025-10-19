import subprocess
import tempfile
import yaml
import os
import json
import re
import logging
import sys
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
import argparse
from dataclasses import dataclass
from enum import Enum

# Third-party imports
from langchain.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI

# UI/UX enhancements
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    from rich.logging import RichHandler
    from rich.tree import Tree
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Rich library not available. Install with: pip install rich")
    print("   Falling back to basic console output.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[RichHandler()] if RICH_AVAILABLE else [logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


# Configuration and Data Classes
@dataclass
class K8sConfig:
    """Configuration for Kubernetes operations"""
    namespace: str = "default"
    api_key: str = ""
    model: str = "gemini-2.0-flash"
    temperature: float = 0.1
    max_tokens: int = 2048
    timeout: int = 30
    max_replicas: int = 10
    allowed_images: List[str] = None
    forbidden_namespaces: List[str] = None
    
    def __post_init__(self):
        if self.allowed_images is None:
            self.allowed_images = ["nginx", "httpd", "redis", "postgres", "mysql", "mongo"]
        if self.forbidden_namespaces is None:
            self.forbidden_namespaces = ["kube-system", "kube-public", "kube-node-lease"]


class K8sOperation(Enum):
    """Supported Kubernetes operations"""
    CREATE_DEPLOYMENT = "create_deployment"
    CREATE_SERVICE = "create_service"
    CREATE_CONFIGMAP = "create_configmap"
    CREATE_SECRET = "create_secret"
    SCALE_DEPLOYMENT = "scale_deployment"
    DELETE_RESOURCE = "delete_resource"
    LIST_RESOURCES = "list_resources"
    GET_LOGS = "get_logs"
    DESCRIBE_RESOURCE = "describe_resource"


class K8sError(Exception):
    """Base exception for Kubernetes operations"""
    pass


class ValidationError(K8sError):
    """Raised when input validation fails"""
    pass


class SecurityError(K8sError):
    """Raised when security checks fail"""
    pass


class ResourceError(K8sError):
    """Raised when resource operations fail"""
    pass


class K8sUI:
    """Enhanced UI/UX for Kubernetes operations"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
    
    def print_header(self, title: str, subtitle: str = ""):
        """Print a beautiful header"""
        if self.console:
            text = Text(title, style="bold blue")
            if subtitle:
                text.append(f"\n{subtitle}", style="dim")
            panel = Panel(text, border_style="blue")
            self.console.print(panel)
        else:
            print(f"\n{'='*50}")
            print(f"🤖 {title}")
            if subtitle:
                print(f"   {subtitle}")
            print(f"{'='*50}")
    
    def print_success(self, message: str):
        """Print success message"""
        if self.console:
            self.console.print(f"✅ {message}", style="green")
        else:
            print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Print error message"""
        if self.console:
            self.console.print(f"❌ {message}", style="red")
        else:
            print(f"❌ {message}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        if self.console:
            self.console.print(f"⚠️  {message}", style="yellow")
        else:
            print(f"⚠️  {message}")
    
    def print_info(self, message: str):
        """Print info message"""
        if self.console:
            self.console.print(f"ℹ️  {message}", style="blue")
        else:
            print(f"ℹ️  {message}")
    
    def show_yaml(self, yaml_content: str, title: str = "Generated YAML"):
        """Display YAML content with syntax highlighting"""
        if self.console:
            syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=True)
            panel = Panel(syntax, title=title, border_style="green")
            self.console.print(panel)
        else:
            print(f"\n{title}:")
            print("-" * len(title))
            print(yaml_content)
    
    def show_table(self, data: List[Dict], title: str = "Resources"):
        """Display data in a table format"""
        if self.console and data:
            table = Table(title=title)
            for key in data[0].keys():
                table.add_column(key, style="cyan")
            for row in data:
                table.add_row(*[str(v) for v in row.values()])
            self.console.print(table)
        else:
            print(f"\n{title}:")
            for item in data:
                print(f"  {item}")


# Input Validation and Guardrails
class InputValidator:
    """Validates and sanitizes user inputs"""
    
    def __init__(self, config: K8sConfig):
        self.config = config
    
    def validate_name(self, name: str) -> str:
        """Validate resource name"""
        if not name:
            raise ValidationError("Name cannot be empty")
        
        # Kubernetes naming rules
        if not re.match(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$', name):
            raise ValidationError("Name must be lowercase alphanumeric with hyphens only")
        
        if len(name) > 63:
            raise ValidationError("Name must be 63 characters or less")
        
        return name.lower().strip()
    
    def validate_image(self, image: str) -> str:
        """Validate container image"""
        if not image:
            raise ValidationError("Image cannot be empty")
        
        # Check if image is in allowed list
        if self.config.allowed_images and not any(allowed in image.lower() for allowed in self.config.allowed_images):
            raise ValidationError(f"Image not in allowed list: {self.config.allowed_images}")
        
        # Basic image format validation
        if not re.match(r'^[a-zA-Z0-9._/-]+(:[a-zA-Z0-9._-]+)?$', image):
            raise ValidationError("Invalid image format")
        
        return image.strip()
    
    def validate_replicas(self, replicas: int) -> int:
        """Validate replica count"""
        if not isinstance(replicas, int) or replicas < 0:
            raise ValidationError("Replicas must be a non-negative integer")
        
        if replicas > self.config.max_replicas:
            raise ValidationError(f"Replicas cannot exceed {self.config.max_replicas}")
        
        return replicas
    
    def validate_namespace(self, namespace: str) -> str:
        """Validate namespace"""
        if not namespace:
            namespace = self.config.namespace
        
        if namespace in self.config.forbidden_namespaces:
            raise SecurityError(f"Namespace '{namespace}' is forbidden")
        
        return self.validate_name(namespace)
    
    def validate_port(self, port: int) -> int:
        """Validate port number"""
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise ValidationError("Port must be between 1 and 65535")
        
        return port


# Enhanced YAML Generation Functions
def generate_deployment_yaml(name: str, image: str, replicas: int = 1, namespace: str = "default", port: int = 80, 
                           cpu_limit: str = "500m", memory_limit: str = "512Mi", env_vars: Dict[str, str] = None):
    """Generate a comprehensive deployment YAML with resource limits and environment variables"""
    containers = [{
        "name": name,
        "image": image,
        "ports": [{"containerPort": port, "name": "http"}],
        "resources": {
            "limits": {"cpu": cpu_limit, "memory": memory_limit},
            "requests": {"cpu": "100m", "memory": "128Mi"}
        },
        "livenessProbe": {
            "httpGet": {"path": "/", "port": port},
            "initialDelaySeconds": 30,
            "periodSeconds": 10
        },
        "readinessProbe": {
            "httpGet": {"path": "/", "port": port},
            "initialDelaySeconds": 5,
            "periodSeconds": 5
        }
    }]
    
    if env_vars:
        containers[0]["env"] = [{"name": k, "value": v} for k, v in env_vars.items()]
    
    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": name, 
            "namespace": namespace,
            "labels": {"app": name, "version": "v1"}
        },
        "spec": {
            "replicas": replicas,
            "selector": {"matchLabels": {"app": name}},
            "template": {
                "metadata": {"labels": {"app": name, "version": "v1"}},
                "spec": {
                    "containers": containers,
                    "restartPolicy": "Always"
                }
            }
        }
    }
    return yaml.dump(deployment, default_flow_style=False, sort_keys=False)


def generate_service_yaml(name: str, port: int = 80, target_port: int = 80, namespace: str = "default", 
                         service_type: str = "ClusterIP"):
    """Generate a service YAML"""
    service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": f"{name}-service",
            "namespace": namespace,
            "labels": {"app": name}
        },
        "spec": {
            "selector": {"app": name},
            "ports": [{"port": port, "targetPort": target_port, "name": "http"}],
            "type": service_type
        }
    }
    return yaml.dump(service, default_flow_style=False, sort_keys=False)


def generate_configmap_yaml(name: str, data: Dict[str, str], namespace: str = "default"):
    """Generate a ConfigMap YAML"""
    configmap = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": f"{name}-config",
            "namespace": namespace,
            "labels": {"app": name}
        },
        "data": data
    }
    return yaml.dump(configmap, default_flow_style=False, sort_keys=False)


def generate_secret_yaml(name: str, data: Dict[str, str], namespace: str = "default"):
    """Generate a Secret YAML"""
    import base64
    encoded_data = {k: base64.b64encode(v.encode()).decode() for k, v in data.items()}
    
    secret = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": f"{name}-secret",
            "namespace": namespace,
            "labels": {"app": name}
        },
        "type": "Opaque",
        "data": encoded_data
    }
    return yaml.dump(secret, default_flow_style=False, sort_keys=False)


# Enhanced kubectl Operations with Error Handling
class K8sOperations:
    """Handles all Kubernetes operations with comprehensive error handling"""
    
    def __init__(self, config: K8sConfig, ui: K8sUI):
        self.config = config
        self.ui = ui
        self.validator = InputValidator(config)
    
    def _run_kubectl(self, cmd: List[str], timeout: int = None) -> Dict[str, Any]:
        """Run kubectl command with error handling"""
        try:
            timeout = timeout or self.config.timeout
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                check=False
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            raise ResourceError(f"kubectl command timed out after {timeout} seconds")
        except FileNotFoundError:
            raise ResourceError("kubectl not found. Please install kubectl and ensure it's in PATH")
        except Exception as e:
            raise ResourceError(f"Failed to run kubectl command: {str(e)}")
    
    def apply_yaml(self, yaml_content: str, dry_run: bool = False) -> Dict[str, Any]:
        """Apply YAML content to Kubernetes cluster"""
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                f.write(yaml_content)
                temp_file = f.name
            
            cmd = ["kubectl", "apply", "-f", temp_file]
            if dry_run:
                cmd.append("--dry-run=client")
            
            result = self._run_kubectl(cmd)
            
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except OSError:
                pass
            
            if not result["success"]:
                raise ResourceError(f"Failed to apply YAML: {result['stderr']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error applying YAML: {str(e)}")
            raise
    
    def delete_resource(self, resource_type: str, name: str, namespace: str = None) -> Dict[str, Any]:
        """Delete a Kubernetes resource"""
        try:
            cmd = ["kubectl", "delete", resource_type, name]
            if namespace:
                cmd.extend(["-n", namespace])
            
            result = self._run_kubectl(cmd)
            
            if not result["success"]:
                raise ResourceError(f"Failed to delete {resource_type} {name}: {result['stderr']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error deleting resource: {str(e)}")
            raise
    
    def list_resources(self, resource_type: str, namespace: str = None) -> List[Dict[str, str]]:
        """List Kubernetes resources"""
        try:
            cmd = ["kubectl", "get", resource_type, "-o", "json"]
            if namespace:
                cmd.extend(["-n", namespace])
            
            result = self._run_kubectl(cmd)
            
            if not result["success"]:
                raise ResourceError(f"Failed to list {resource_type}: {result['stderr']}")
            
            data = json.loads(result["stdout"])
            resources = []
            
            for item in data.get("items", []):
                metadata = item.get("metadata", {})
                resources.append({
                    "name": metadata.get("name", ""),
                    "namespace": metadata.get("namespace", ""),
                    "age": metadata.get("creationTimestamp", ""),
                    "status": item.get("status", {}).get("phase", "")
                })
            
            return resources
            
        except Exception as e:
            logger.error(f"Error listing resources: {str(e)}")
            raise
    
    def get_logs(self, pod_name: str, namespace: str = None, lines: int = 100) -> str:
        """Get logs from a pod"""
        try:
            cmd = ["kubectl", "logs", pod_name, f"--tail={lines}"]
            if namespace:
                cmd.extend(["-n", namespace])
            
            result = self._run_kubectl(cmd)
            
            if not result["success"]:
                raise ResourceError(f"Failed to get logs for {pod_name}: {result['stderr']}")
            
            return result["stdout"]
            
        except Exception as e:
            logger.error(f"Error getting logs: {str(e)}")
            raise
    
    def describe_resource(self, resource_type: str, name: str, namespace: str = None) -> str:
        """Describe a Kubernetes resource"""
        try:
            cmd = ["kubectl", "describe", resource_type, name]
            if namespace:
                cmd.extend(["-n", namespace])
            
            result = self._run_kubectl(cmd)
            
            if not result["success"]:
                raise ResourceError(f"Failed to describe {resource_type} {name}: {result['stderr']}")
            
            return result["stdout"]
            
        except Exception as e:
            logger.error(f"Error describing resource: {str(e)}")
            raise
    
    def scale_deployment(self, name: str, replicas: int, namespace: str = None) -> Dict[str, Any]:
        """Scale a deployment"""
        try:
            replicas = self.validator.validate_replicas(replicas)
            
            cmd = ["kubectl", "scale", "deployment", name, f"--replicas={replicas}"]
            if namespace:
                cmd.extend(["-n", namespace])
            
            result = self._run_kubectl(cmd)
            
            if not result["success"]:
                raise ResourceError(f"Failed to scale deployment {name}: {result['stderr']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error scaling deployment: {str(e)}")
            raise


# Enhanced LangChain Tools
class CreateDeploymentTool(BaseTool):
    name: str = "create_deployment"
    description: str = """Create a Kubernetes deployment with comprehensive configuration.
    Input format: JSON with keys: name (str), image (str), replicas (int, default 1), 
    namespace (str, default 'default'), port (int, default 80), cpu_limit (str, default '500m'),
    memory_limit (str, default '512Mi'), env_vars (dict, optional)"""
    
    k8s_ops: K8sOperations
    ui: K8sUI

    def __init__(self, k8s_ops: K8sOperations, ui: K8sUI):
        super().__init__(k8s_ops=k8s_ops, ui=ui)

    def _run(self, tool_input: str) -> str:
        """Create a Kubernetes deployment with validation and error handling"""
        try:
            data = json.loads(tool_input)
            
            # Validate and sanitize inputs
            name = self.k8s_ops.validator.validate_name(data.get('name'))
            image = self.k8s_ops.validator.validate_image(data.get('image'))
            replicas = self.k8s_ops.validator.validate_replicas(data.get('replicas', 1))
            namespace = self.k8s_ops.validator.validate_namespace(data.get('namespace', 'default'))
            port = self.k8s_ops.validator.validate_port(data.get('port', 80))
            cpu_limit = data.get('cpu_limit', '500m')
            memory_limit = data.get('memory_limit', '512Mi')
            env_vars = data.get('env_vars', {})
            
            # Generate YAML
            yaml_content = generate_deployment_yaml(
                name, image, replicas, namespace, port, cpu_limit, memory_limit, env_vars
            )
            
            # Show generated YAML
            self.ui.show_yaml(yaml_content, f"Deployment YAML for {name}")
            
            # Apply to cluster
            result = self.k8s_ops.apply_yaml(yaml_content)
            
            self.ui.print_success(f"Deployment '{name}' created successfully in namespace '{namespace}'")
            return f"Deployment created: {result['stdout']}"
            
        except ValidationError as e:
            self.ui.print_error(f"Validation error: {str(e)}")
            return f"Validation error: {str(e)}"
        except SecurityError as e:
            self.ui.print_error(f"Security error: {str(e)}")
            return f"Security error: {str(e)}"
        except ResourceError as e:
            self.ui.print_error(f"Resource error: {str(e)}")
            return f"Resource error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in CreateDeploymentTool: {str(e)}")
            self.ui.print_error(f"Unexpected error: {str(e)}")
            return f"Error: {str(e)}"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError()


class CreateServiceTool(BaseTool):
    name: str = "create_service"
    description: str = """Create a Kubernetes service for a deployment.
    Input format: JSON with keys: name (str), port (int, default 80), 
    target_port (int, default 80), namespace (str, default 'default'),
    service_type (str, default 'ClusterIP')"""
    
    k8s_ops: K8sOperations
    ui: K8sUI

    def __init__(self, k8s_ops: K8sOperations, ui: K8sUI):
        super().__init__(k8s_ops=k8s_ops, ui=ui)

    def _run(self, tool_input: str) -> str:
        try:
            data = json.loads(tool_input)
            
            name = self.k8s_ops.validator.validate_name(data.get('name'))
            port = self.k8s_ops.validator.validate_port(data.get('port', 80))
            target_port = self.k8s_ops.validator.validate_port(data.get('target_port', 80))
            namespace = self.k8s_ops.validator.validate_namespace(data.get('namespace', 'default'))
            service_type = data.get('service_type', 'ClusterIP')
            
            yaml_content = generate_service_yaml(name, port, target_port, namespace, service_type)
            
            self.ui.show_yaml(yaml_content, f"Service YAML for {name}")
            
            result = self.k8s_ops.apply_yaml(yaml_content)
            
            self.ui.print_success(f"Service '{name}-service' created successfully")
            return f"Service created: {result['stdout']}"
            
        except Exception as e:
            logger.error(f"Error in CreateServiceTool: {str(e)}")
            self.ui.print_error(f"Error creating service: {str(e)}")
            return f"Error: {str(e)}"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError()


class ListResourcesTool(BaseTool):
    name: str = "list_resources"
    description: str = """List Kubernetes resources.
    Input format: JSON with keys: resource_type (str), namespace (str, optional)"""
    
    k8s_ops: K8sOperations
    ui: K8sUI

    def __init__(self, k8s_ops: K8sOperations, ui: K8sUI):
        super().__init__(k8s_ops=k8s_ops, ui=ui)

    def _run(self, tool_input: str) -> str:
        try:
            data = json.loads(tool_input)
            
            resource_type = data.get('resource_type', 'pods')
            namespace = data.get('namespace')
            
            resources = self.k8s_ops.list_resources(resource_type, namespace)
            
            if resources:
                self.ui.show_table(resources, f"{resource_type.title()} Resources")
                return f"Found {len(resources)} {resource_type}"
            else:
                self.ui.print_info(f"No {resource_type} found")
                return f"No {resource_type} found"
                
        except Exception as e:
            logger.error(f"Error in ListResourcesTool: {str(e)}")
            self.ui.print_error(f"Error listing resources: {str(e)}")
            return f"Error: {str(e)}"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError()


class ScaleDeploymentTool(BaseTool):
    name: str = "scale_deployment"
    description: str = """Scale a Kubernetes deployment.
    Input format: JSON with keys: name (str), replicas (int), namespace (str, optional)"""
    
    k8s_ops: K8sOperations
    ui: K8sUI

    def __init__(self, k8s_ops: K8sOperations, ui: K8sUI):
        super().__init__(k8s_ops=k8s_ops, ui=ui)

    def _run(self, tool_input: str) -> str:
        try:
            data = json.loads(tool_input)
            
            name = self.k8s_ops.validator.validate_name(data.get('name'))
            replicas = self.k8s_ops.validator.validate_replicas(data.get('replicas'))
            namespace = data.get('namespace')
            
            result = self.k8s_ops.scale_deployment(name, replicas, namespace)
            
            self.ui.print_success(f"Deployment '{name}' scaled to {replicas} replicas")
            return f"Deployment scaled: {result['stdout']}"
            
        except Exception as e:
            logger.error(f"Error in ScaleDeploymentTool: {str(e)}")
            self.ui.print_error(f"Error scaling deployment: {str(e)}")
            return f"Error: {str(e)}"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError()


class GetLogsTool(BaseTool):
    name: str = "get_logs"
    description: str = """Get logs from a Kubernetes pod.
    Input format: JSON with keys: pod_name (str), namespace (str, optional), lines (int, default 100)"""
    
    k8s_ops: K8sOperations
    ui: K8sUI

    def __init__(self, k8s_ops: K8sOperations, ui: K8sUI):
        super().__init__(k8s_ops=k8s_ops, ui=ui)

    def _run(self, tool_input: str) -> str:
        try:
            data = json.loads(tool_input)
            
            pod_name = data.get('pod_name')
            namespace = data.get('namespace')
            lines = data.get('lines', 100)
            
            if not pod_name:
                raise ValidationError("pod_name is required")
            
            logs = self.k8s_ops.get_logs(pod_name, namespace, lines)
            
            if logs:
                self.ui.print_info(f"Logs from pod '{pod_name}':")
                print(logs)
                return f"Retrieved {len(logs.splitlines())} log lines"
            else:
                self.ui.print_info(f"No logs found for pod '{pod_name}'")
                return "No logs found"
                
        except Exception as e:
            logger.error(f"Error in GetLogsTool: {str(e)}")
            self.ui.print_error(f"Error getting logs: {str(e)}")
            return f"Error: {str(e)}"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError()


# Enhanced Agent Setup
class K8sAgent:
    """Enhanced Kubernetes Agent with comprehensive features"""
    
    def __init__(self, config: K8sConfig):
        self.config = config
        self.ui = K8sUI()
        self.k8s_ops = K8sOperations(config, self.ui)
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=config.model,
            google_api_key=config.api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
        
        # Initialize tools
        self.tools = self._create_tools()
        
        # Create agent
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[BaseTool]:
        """Create all available tools"""
        return [
            CreateDeploymentTool(self.k8s_ops, self.ui),
            CreateServiceTool(self.k8s_ops, self.ui),
            ListResourcesTool(self.k8s_ops, self.ui),
            ScaleDeploymentTool(self.k8s_ops, self.ui),
            GetLogsTool(self.k8s_ops, self.ui)
        ]
    
    def _create_agent(self):
        """Create a simplified agent that processes user input and calls appropriate tools"""
        return None  # We'll handle this in the run method
    
    def run(self, user_input: str) -> str:
        """Run the agent with user input"""
        try:
            # Validate input
            if not user_input.strip():
                self.ui.print_warning("Please provide a valid command")
                return "No input provided"
            
            # Check for dangerous commands
            dangerous_keywords = ["delete", "remove", "destroy", "kill"]
            if any(keyword in user_input.lower() for keyword in dangerous_keywords):
                self.ui.print_warning("⚠️  This command may modify or delete resources. Please review carefully.")
            
            # Simple command processing
            user_input_lower = user_input.lower()
            
            # Handle help commands
            if any(cmd in user_input_lower for cmd in ["help", "h", "?"]):
                self.show_help()
                return "Help displayed"
            
            # Handle status commands
            if any(cmd in user_input_lower for cmd in ["status", "info"]):
                self.show_status()
                return "Status displayed"
            
            # Process deployment commands
            if "create" in user_input_lower and "deployment" in user_input_lower:
                return self._process_deployment_command(user_input)
            
            # Process service commands
            if "create" in user_input_lower and "service" in user_input_lower:
                return self._process_service_command(user_input)
            
            # Process list commands
            if "list" in user_input_lower:
                return self._process_list_command(user_input)
            
            # Process scale commands
            if "scale" in user_input_lower:
                return self._process_scale_command(user_input)
            
            # Process logs commands
            if "log" in user_input_lower:
                return self._process_logs_command(user_input)
            
            # Default response
            return "I understand you want to work with Kubernetes. Please be more specific about what you'd like to do. Try 'help' for available commands."
            
        except Exception as e:
            logger.error(f"Error in agent execution: {str(e)}")
            self.ui.print_error(f"Agent error: {str(e)}")
            return f"Error: {str(e)}"
    
    def _process_deployment_command(self, user_input: str) -> str:
        """Process deployment creation commands"""
        try:
            # Simple parsing - look for name, image, replicas
            import re
            
            # Extract name
            name_match = re.search(r"named?\s+['\"]?(\w+)['\"]?", user_input, re.IGNORECASE)
            name = name_match.group(1) if name_match else "webapp"
            
            # Extract image
            image_match = re.search(r"(\w+)(?::\w+)?\s+image", user_input, re.IGNORECASE)
            if not image_match:
                image_match = re.search(r"image\s+(\w+)(?::\w+)?", user_input, re.IGNORECASE)
            image = image_match.group(1) if image_match else "nginx"
            
            # Extract replicas
            replicas_match = re.search(r"(\d+)\s+replicas?", user_input, re.IGNORECASE)
            replicas = int(replicas_match.group(1)) if replicas_match else 1
            
            # Create deployment
            tool = CreateDeploymentTool(self.k8s_ops, self.ui)
            tool_input = json.dumps({
                "name": name,
                "image": image,
                "replicas": replicas
            })
            return tool._run(tool_input)
            
        except Exception as e:
            return f"Error processing deployment command: {str(e)}"
    
    def _process_service_command(self, user_input: str) -> str:
        """Process service creation commands"""
        try:
            # Simple parsing
            import re
            
            name_match = re.search(r"for\s+['\"]?(\w+)['\"]?", user_input, re.IGNORECASE)
            name = name_match.group(1) if name_match else "webapp"
            
            port_match = re.search(r"port\s+(\d+)", user_input, re.IGNORECASE)
            port = int(port_match.group(1)) if port_match else 80
            
            tool = CreateServiceTool(self.k8s_ops, self.ui)
            tool_input = json.dumps({
                "name": name,
                "port": port
            })
            return tool._run(tool_input)
            
        except Exception as e:
            return f"Error processing service command: {str(e)}"
    
    def _process_list_command(self, user_input: str) -> str:
        """Process list commands"""
        try:
            resource_type = "pods"
            if "deployment" in user_input.lower():
                resource_type = "deployments"
            elif "service" in user_input.lower():
                resource_type = "services"
            
            tool = ListResourcesTool(self.k8s_ops, self.ui)
            tool_input = json.dumps({
                "resource_type": resource_type
            })
            return tool._run(tool_input)
            
        except Exception as e:
            return f"Error processing list command: {str(e)}"
    
    def _process_scale_command(self, user_input: str) -> str:
        """Process scale commands"""
        try:
            import re
            
            name_match = re.search(r"['\"]?(\w+)['\"]?\s+deployment", user_input, re.IGNORECASE)
            name = name_match.group(1) if name_match else "webapp"
            
            replicas_match = re.search(r"(\d+)\s+replicas?", user_input, re.IGNORECASE)
            replicas = int(replicas_match.group(1)) if replicas_match else 1
            
            tool = ScaleDeploymentTool(self.k8s_ops, self.ui)
            tool_input = json.dumps({
                "name": name,
                "replicas": replicas
            })
            return tool._run(tool_input)
            
        except Exception as e:
            return f"Error processing scale command: {str(e)}"
    
    def _process_logs_command(self, user_input: str) -> str:
        """Process logs commands"""
        try:
            import re
            
            pod_match = re.search(r"pod\s+['\"]?(\w+)['\"]?", user_input, re.IGNORECASE)
            pod_name = pod_match.group(1) if pod_match else "webapp"
            
            tool = GetLogsTool(self.k8s_ops, self.ui)
            tool_input = json.dumps({
                "pod_name": pod_name
            })
            return tool._run(tool_input)
            
        except Exception as e:
            return f"Error processing logs command: {str(e)}"
    
    def show_help(self):
        """Show available commands and help"""
        help_text = """
🤖 Kubernetes AI Agent - Available Commands:

📦 DEPLOYMENT OPERATIONS:
  • Create deployment: "Create a deployment named 'webapp' with nginx image and 3 replicas"
  • Scale deployment: "Scale the 'webapp' deployment to 5 replicas"
  • List deployments: "List all deployments in the default namespace"

🌐 SERVICE OPERATIONS:
  • Create service: "Create a service for the 'webapp' deployment on port 80"
  • List services: "List all services"

📋 RESOURCE MANAGEMENT:
  • List pods: "List all pods"
  • Get logs: "Get logs from pod 'webapp-xxx'"
  • List all resources: "List all resources in the cluster"

🔧 CONFIGURATION:
  • Set namespace: "Use namespace 'production'"
  • Show configuration: "Show current configuration"

💡 EXAMPLES:
  • "Create a deployment called 'api' using the 'node:18' image with 2 replicas"
  • "Scale the 'api' deployment to 5 replicas"
  • "Create a service for 'api' on port 3000"
  • "List all pods in the 'production' namespace"
  • "Get the last 50 lines of logs from pod 'api-xxx'"

Type 'exit' or 'quit' to stop the agent.
        """
        self.ui.print_info(help_text)
    
    def show_status(self):
        """Show agent and cluster status"""
        try:
            # Test kubectl connectivity
            result = self.k8s_ops._run_kubectl(["kubectl", "version", "--client"])
            if result["success"]:
                self.ui.print_success("✅ kubectl is available and working")
            else:
                self.ui.print_error("❌ kubectl is not available or not working")
            
            # Show configuration
            config_info = f"""
Current Configuration:
  • Model: {self.config.model}
  • Namespace: {self.config.namespace}
  • Max Replicas: {self.config.max_replicas}
  • Allowed Images: {', '.join(self.config.allowed_images)}
  • Forbidden Namespaces: {', '.join(self.config.forbidden_namespaces)}
            """
            self.ui.print_info(config_info)
            
        except Exception as e:
            self.ui.print_error(f"Error checking status: {str(e)}")

# Configuration and CLI Setup
def load_config() -> K8sConfig:
    """Load configuration from environment or use defaults"""
    api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyB3nDVLSAgxmNQdi1ksiE1oNLi8ITgIf4o")
    
    return K8sConfig(
        api_key=api_key,
        model=os.getenv("K8S_MODEL", "gemini-2.0-flash"),
        temperature=float(os.getenv("K8S_TEMPERATURE", "0.1")),
        max_tokens=int(os.getenv("K8S_MAX_TOKENS", "2048")),
        namespace=os.getenv("K8S_NAMESPACE", "default"),
        max_replicas=int(os.getenv("K8S_MAX_REPLICAS", "10"))
    )


def main():
    """Main application entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Enhanced Kubernetes AI Agent")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--namespace", help="Default namespace to use")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Load configuration
        config = load_config()
        if args.namespace:
            config.namespace = args.namespace
        
        # Initialize agent
        agent = K8sAgent(config)
        
        # Show welcome message
        agent.ui.print_header(
            "🚀 Enhanced Kubernetes AI Agent",
            "Powered by LangChain and Google Gemini"
        )
        
        # Show status
        agent.show_status()
        
        # Interactive loop
        while True:
            try:
                if RICH_AVAILABLE:
                    user_input = Prompt.ask("\n💡 What should I do?", default="help")
                else:
                    user_input = input("\n💡 What should I do? (or 'help', 'exit'): ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ["exit", "quit", "q"]:
                    agent.ui.print_info("👋 Goodbye!")
                    break
                elif user_input.lower() in ["help", "h", "?"]:
                    agent.show_help()
                    continue
                elif user_input.lower() in ["status", "info"]:
                    agent.show_status()
                    continue
                elif user_input.lower() in ["clear", "cls"]:
                    if RICH_AVAILABLE:
                        agent.ui.console.clear()
                    else:
                        os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                
                # Run agent
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=agent.ui.console if RICH_AVAILABLE else None
                ) as progress:
                    task = progress.add_task("Processing...", total=None)
                    result = agent.run(user_input)
                    progress.update(task, completed=True)
                
                # Show result
                if result and result != "No response generated":
                    agent.ui.print_success("✅ Operation completed")
                    print(f"\nResult: {result}")
                
            except KeyboardInterrupt:
                agent.ui.print_warning("\n⚠️  Interrupted by user")
                continue
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                agent.ui.print_error(f"Unexpected error: {str(e)}")
                print("Please try again or type 'exit' to quit")
    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)


# Run
if __name__ == "__main__":
    main()
