from fastapi import APIRouter, HTTPException
from app.models.schemas import UserLogin, UserLoginResponse, InteractionFeedback
from app.services.user_service import user_service
import secrets

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=UserLoginResponse)
async def login(login_data: UserLogin):
    """Login do usuário (cria se não existir)"""
    try:
        user = user_service.get_or_create_user(
            username=login_data.username,
            email=login_data.email
        )
        
        # Gera token simples (em produção use JWT)
        token = secrets.token_urlsafe(32)
        
        return UserLoginResponse(
            user=user,
            token=token,
            message=f"Bem-vindo, {user.username}!"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no login: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_info(user_id: str):
    """Obtém informações e contexto do usuário"""
    try:
        context = user_service.get_user_context(user_id)
        return context
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/feedback")
async def submit_feedback(feedback_data: InteractionFeedback):
    """Envia feedback sobre uma interação"""
    try:
        user_service.update_interaction_feedback(
            interaction_id=feedback_data.interaction_id,
            feedback=feedback_data.feedback,
            comment=feedback_data.comment
        )
        return {"message": "Feedback registrado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")
