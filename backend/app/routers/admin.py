from fastapi import APIRouter, HTTPException
from app.services.google_sheets import sheets_service
from app.services.rag_service import rag_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/refresh")
async def refresh_rag():
    """Recarrega os dados do Google Sheets e reindexa o RAG sem reiniciar o servidor"""
    try:
        print("🔄 Refresh manual iniciado...")

        sheets_service.invalidate_cache()
        equipments = sheets_service.get_all_equipments(force_refresh=True)

        rag_service.index_equipments(equipments)

        return {
            "status": "ok",
            "message": f"{len(equipments)} equipamentos reindexados com sucesso.",
            "areas": sheets_service.get_available_areas(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no refresh: {str(e)}")
