from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import settings
# Adicione analytics aqui
from app.routers import chat, auth, analytics, admin
from app.services.google_sheets import sheets_service
from app.services.rag_service import rag_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia inicialização"""
    print("🚀 Iniciando Industrial AI Agent...")
    
    try:
        print("📊 Aquecendo cache dos equipamentos...")
        equipments = sheets_service.get_all_equipments()

        if rag_service.vectorstore is None:
            print("🔍 Indexando no RAG pela primeira vez...")
            rag_service.index_equipments(equipments)
        else:
            print("✅ Vector store já carregado — use POST /api/v1/admin/refresh para reindexar.")

        print("✅ Sistema pronto!")
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
    
    yield
    
    print("👋 Encerrando...")

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix=settings.API_PREFIX)
app.include_router(auth.router, prefix=settings.API_PREFIX)
# Adicione esta linha
app.include_router(analytics.router, prefix=settings.API_PREFIX)
app.include_router(admin.router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Industrial AI Agent - UNS API",
        "version": settings.API_VERSION,
        "status": "online"
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "services": {
            "google_sheets": sheets_service.client is not None,
            "rag": rag_service.vectorstore is not None
        }
    }