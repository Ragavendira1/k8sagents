"""
FastAPI Backend for Kubernetes AI Agent Web Interface
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json
import logging
import sys
import os
from datetime import datetime

# Add parent directory to path to import k8s modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from k8s import K8sConfig, K8sAgent, K8sUI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Kubernetes AI Agent API",
    description="REST API for Kubernetes AI Agent with LangChain and Google Gemini",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
k8s_agent = None
active_connections: List[WebSocket] = []

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    timestamp: Optional[datetime] = None

class DeploymentRequest(BaseModel):
    name: str
    image: str
    replicas: int = 1
    namespace: str = "default"
    port: int = 80
    cpu_limit: str = "500m"
    memory_limit: str = "512Mi"
    env_vars: Optional[Dict[str, str]] = None

class ServiceRequest(BaseModel):
    name: str
    port: int = 80
    target_port: int = 80
    namespace: str = "default"
    service_type: str = "ClusterIP"

class ScaleRequest(BaseModel):
    name: str
    replicas: int
    namespace: Optional[str] = None

class LogsRequest(BaseModel):
    pod_name: str
    namespace: Optional[str] = None
    lines: int = 100

# Initialize K8s Agent
@app.on_event("startup")
async def startup_event():
    """Initialize the Kubernetes agent on startup"""
    global k8s_agent
    try:
        config = K8sConfig(
            api_key=os.getenv("GOOGLE_API_KEY", "AIzaSyB3nDVLSAgxmNQdi1ksiE1oNLi8ITgIf4o"),
            model=os.getenv("K8S_MODEL", "gemini-2.0-flash"),
            temperature=float(os.getenv("K8S_TEMPERATURE", "0.1")),
            max_tokens=int(os.getenv("K8S_MAX_TOKENS", "2048")),
            namespace=os.getenv("K8S_NAMESPACE", "default"),
            max_replicas=int(os.getenv("K8S_MAX_REPLICAS", "10"))
        )
        k8s_agent = K8sAgent(config)
        logger.info("Kubernetes AI Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize K8s Agent: {str(e)}")
        raise

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Kubernetes AI Agent API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_initialized": k8s_agent is not None
    }

@app.get("/api/status")
async def get_status():
    """Get agent and cluster status"""
    if not k8s_agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # Test kubectl connectivity
        result = k8s_agent.k8s_ops._run_kubectl(["kubectl", "version", "--client"])
        kubectl_status = result["success"]
        
        return {
            "agent_status": "running",
            "kubectl_available": kubectl_status,
            "configuration": {
                "model": k8s_agent.config.model,
                "namespace": k8s_agent.config.namespace,
                "max_replicas": k8s_agent.config.max_replicas,
                "allowed_images": k8s_agent.config.allowed_images,
                "forbidden_namespaces": k8s_agent.config.forbidden_namespaces
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.post("/api/chat")
async def chat_with_agent(message: ChatMessage):
    """Chat with the AI agent"""
    if not k8s_agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        response = k8s_agent.run(message.message)
        return {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/api/deployments")
async def create_deployment(deployment: DeploymentRequest):
    """Create a Kubernetes deployment"""
    if not k8s_agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        tool = k8s_agent.tools[0]  # CreateDeploymentTool
        tool_input = json.dumps({
            "name": deployment.name,
            "image": deployment.image,
            "replicas": deployment.replicas,
            "namespace": deployment.namespace,
            "port": deployment.port,
            "cpu_limit": deployment.cpu_limit,
            "memory_limit": deployment.memory_limit,
            "env_vars": deployment.env_vars or {}
        })
        
        result = tool._run(tool_input)
        
        return {
            "message": f"Deployment '{deployment.name}' created successfully",
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Deployment creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deployment creation failed: {str(e)}")

@app.post("/api/services")
async def create_service(service: ServiceRequest):
    """Create a Kubernetes service"""
    if not k8s_agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        tool = k8s_agent.tools[1]  # CreateServiceTool
        tool_input = json.dumps({
            "name": service.name,
            "port": service.port,
            "target_port": service.target_port,
            "namespace": service.namespace,
            "service_type": service.service_type
        })
        
        result = tool._run(tool_input)
        
        return {
            "message": f"Service '{service.name}' created successfully",
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Service creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service creation failed: {str(e)}")

@app.get("/api/resources/{resource_type}")
async def list_resources(resource_type: str, namespace: Optional[str] = None):
    """List Kubernetes resources"""
    if not k8s_agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        tool = k8s_agent.tools[2]  # ListResourcesTool
        tool_input = json.dumps({
            "resource_type": resource_type,
            "namespace": namespace
        })
        
        result = tool._run(tool_input)
        resources = k8s_agent.k8s_ops.list_resources(resource_type, namespace)
        
        return {
            "resources": resources,
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"List resources error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"List resources failed: {str(e)}")

@app.post("/api/scale")
async def scale_deployment(scale: ScaleRequest):
    """Scale a Kubernetes deployment"""
    if not k8s_agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        tool = k8s_agent.tools[3]  # ScaleDeploymentTool
        tool_input = json.dumps({
            "name": scale.name,
            "replicas": scale.replicas,
            "namespace": scale.namespace
        })
        
        result = tool._run(tool_input)
        
        return {
            "message": f"Deployment '{scale.name}' scaled to {scale.replicas} replicas",
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Scale deployment error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scale deployment failed: {str(e)}")

@app.post("/api/logs")
async def get_logs(logs_request: LogsRequest):
    """Get logs from a Kubernetes pod"""
    if not k8s_agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        tool = k8s_agent.tools[4]  # GetLogsTool
        tool_input = json.dumps({
            "pod_name": logs_request.pod_name,
            "namespace": logs_request.namespace,
            "lines": logs_request.lines
        })
        
        result = tool._run(tool_input)
        
        return {
            "logs": result,
            "pod_name": logs_request.pod_name,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Get logs error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get logs failed: {str(e)}")

# WebSocket endpoint for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "chat":
                # Process chat message
                if k8s_agent:
                    response = k8s_agent.run(message_data["message"])
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "response",
                            "message": response,
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
                else:
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "error",
                            "message": "Agent not initialized",
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
            
            elif message_data.get("type") == "status":
                # Send status update
                status = {
                    "type": "status",
                    "agent_initialized": k8s_agent is not None,
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(json.dumps(status), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)