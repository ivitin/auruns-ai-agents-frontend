from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Equipment(BaseModel):
    """Modelo para equipamentos industriais"""
    nivel: Optional[str] = None
    local: Optional[str] = None
    localizacao: Optional[str] = None
    ute: Optional[str] = None
    linha: Optional[str] = None
    operacao: Optional[str] = None
    estacao: Optional[str] = None
    maquina: Optional[str] = None
    equipamento: Optional[str] = None
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    denominacao: Optional[str] = None
    tipo: Optional[str] = None
    area: str

class ChatMessage(BaseModel):
    """Mensagem de chat"""
    role: str = Field(..., description="Papel: user ou assistant")
    content: str = Field(..., description="Conteúdo da mensagem")
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatRequest(BaseModel):
    """Request para o chat"""
    message: str = Field(..., description="Mensagem do usuário")
    conversation_id: Optional[str] = Field(None, description="ID da conversa")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChatResponse(BaseModel):
    """Resposta do chat"""
    response: str = Field(..., description="Resposta do agente")
    conversation_id: str = Field(..., description="ID da conversa")
    sources: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class EquipmentQuery(BaseModel):
    """Query para buscar equipamentos"""
    query: str = Field(..., description="Consulta em linguagem natural")
    filters: Optional[Dict[str, str]] = Field(default_factory=dict)
    limit: int = Field(10, description="Limite de resultados")

class EquipmentQueryResponse(BaseModel):
    """Resposta da query de equipamentos"""
    equipments: List[Equipment]
    total: int
    query: str
    interpretation: str = Field(..., description="Interpretação da query")

class UNSArchitectureRequest(BaseModel):
    """Request para gerar arquitetura UNS"""
    area: Optional[str] = Field(None, description="Filtrar por área específica")
    format: str = Field("json", description="Formato: json, text, mermaid")
    max_depth: int = Field(5, description="Profundidade máxima da árvore")

class UNSArchitectureResponse(BaseModel):
    """Resposta com arquitetura UNS"""
    architecture: Any = Field(..., description="Arquitetura no formato solicitado")
    statistics: Dict[str, Any] = Field(..., description="Estatísticas da arquitetura")
    format: str = Field(..., description="Formato retornado")

# User Models
class User(BaseModel):
    """Modelo de usuário"""
    user_id: str = Field(..., description="ID único do usuário")
    username: str = Field(..., description="Nome de usuário")
    email: Optional[str] = Field(None, description="Email do usuário")
    created_at: str = Field(..., description="Data de criação")
    last_login: Optional[str] = Field(None, description="Último login")
    role: str = Field(default="user", description="Papel do usuário")

class UserLogin(BaseModel):
    """Request de login"""
    username: str = Field(..., description="Nome de usuário")
    email: Optional[str] = Field(None, description="Email opcional")

class UserLoginResponse(BaseModel):
    """Resposta de login"""
    user: User
    token: str = Field(..., description="Token de sessão")
    message: str = Field(..., description="Mensagem de sucesso")

# Interaction Models
class Interaction(BaseModel):
    """Modelo de interação"""
    interaction_id: str = Field(..., description="ID da interação")
    user_id: str = Field(..., description="ID do usuário")
    conversation_id: str = Field(..., description="ID da conversa")
    timestamp: str = Field(..., description="Timestamp da interação")
    user_message: str = Field(..., description="Mensagem do usuário")
    agent_response: str = Field(..., description="Resposta do agente")
    sources: Optional[str] = Field(None, description="Fontes consultadas (JSON)")
    feedback: Optional[str] = Field(None, description="Feedback: positive, negative, ou null")
    metadata: Optional[str] = Field(None, description="Metadados adicionais (JSON)")

class InteractionFeedback(BaseModel):
    """Feedback de uma interação"""
    interaction_id: str = Field(..., description="ID da interação")
    feedback: str = Field(..., description="positive ou negative")
    comment: Optional[str] = Field(None, description="Comentário opcional")

class UserContext(BaseModel):
    """Contexto do usuário baseado em histórico"""
    user_id: str
    recent_interactions: List[Dict[str, Any]] = Field(default_factory=list)
    common_topics: List[str] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)

# Analytics Models
class AnalyticsReport(BaseModel):
    """Relatório completo de analytics"""
    generated_at: str
    overall: Dict[str, Any]
    usage: Dict[str, Any]
    content: Dict[str, Any]
    performance: Dict[str, Any]
    engagement: Dict[str, Any]
