from fastapi import APIRouter, HTTPException
from app.services.analytics_service import analytics_service
from app.models.schemas import AnalyticsReport

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/overall")
async def get_overall_metrics():
    """Métricas gerais do sistema"""
    try:
        return analytics_service.get_overall_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage")
async def get_usage_metrics():
    """Métricas de uso e padrões"""
    try:
        return analytics_service.get_usage_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content")
async def get_content_metrics():
    """Métricas sobre conteúdo consultado"""
    try:
        return analytics_service.get_content_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance_metrics():
    """Métricas de performance do LLM"""
    try:
        return analytics_service.get_performance_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/engagement")
async def get_engagement_metrics():
    """Métricas de engajamento dos usuários"""
    try:
        return analytics_service.get_user_engagement_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report", response_model=AnalyticsReport)
async def get_full_report():
    """Relatório completo de analytics"""
    try:
        return analytics_service.generate_full_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
