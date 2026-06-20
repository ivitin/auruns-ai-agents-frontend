from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List, Dict, Any
from app.config.settings import settings
from app.models.schemas import Equipment
from app.utils.nlp_utils import classify_equipment_type
import json

class RAGService:
    """Serviço para Retrieval Augmented Generation"""
    
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.text_splitter = None
        self._initialize_rag()
    
    def _initialize_rag(self):
        """Inicializa componentes RAG"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )

            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )

            # Try to load existing vectorstore
            try:
                self.load_vectorstore()
            except:
                pass  # Vectorstore will be created when indexing

            print("✅ RAG inicializado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao inicializar RAG: {e}")
            raise
    
    def equipment_to_document(self, equipment: Equipment) -> Document:
        """Converte Equipment para Document do LangChain"""
        text_parts = []
        
        if equipment.area:
            text_parts.append(f"Área: {equipment.area}")
        if equipment.ute:
            text_parts.append(f"UTE: {equipment.ute}")
        if equipment.linha:
            text_parts.append(f"Linha: {equipment.linha}")
        if equipment.estacao:
            text_parts.append(f"Estação: {equipment.estacao}")
        if equipment.maquina:
            text_parts.append(f"Máquina: {equipment.maquina}")
        if equipment.codigo:
            text_parts.append(f"Código: {equipment.codigo}")
        if equipment.descricao:
            text_parts.append(f"Descrição: {equipment.descricao}")
        if equipment.denominacao:
            text_parts.append(f"Denominação: {equipment.denominacao}")
        if equipment.operacao:
            text_parts.append(f"Operação: {equipment.operacao}")
        
        text = "\n".join(text_parts)
        
        tipo_classificado = classify_equipment_type(
            descricao=equipment.descricao or "",
            maquina=equipment.maquina or "",
            denominacao=equipment.denominacao or "",
        )

        metadata = {
            "area": equipment.area or "",
            "codigo": equipment.codigo or "",
            "ute": equipment.ute or "",
            "linha": equipment.linha or "",
            "tipo": tipo_classificado,
        }
        
        return Document(page_content=text, metadata=metadata)
    
    def index_equipments(self, equipments: List[Equipment]):
        """Indexa equipamentos no vector store"""
        try:
            documents = [self.equipment_to_document(eq) for eq in equipments]
            
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY
            )
            
            print(f"✅ {len(documents)} equipamentos indexados no vector store!")
            
        except Exception as e:
            print(f"❌ Erro ao indexar equipamentos: {e}")
            raise
    
    def load_vectorstore(self):
        """Carrega vector store existente"""
        try:
            self.vectorstore = Chroma(
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
                embedding_function=self.embeddings
            )
            print("✅ Vector store carregado!")
        except Exception as e:
            print(f"⚠️ Vector store não encontrado: {e}")
    
    def semantic_search(
        self, 
        query: str, 
        k: int = 5, 
        filter_dict: Dict[str, str] = None
    ) -> List[Dict[str, Any]]:
        """Busca semântica por equipamentos"""
        try:
            if not self.vectorstore:
                return []

            if filter_dict:
                try:
                    results = self.vectorstore.similarity_search(query, k=k, filter=filter_dict)
                except Exception as filter_err:
                    print(f"⚠️  Filtro falhou ({filter_err}), tentando sem filtro...")
                    results = self.vectorstore.similarity_search(query, k=k)
            else:
                results = self.vectorstore.similarity_search(query, k=k)

            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })

            return formatted_results

        except Exception as e:
            print(f"❌ Erro na busca semântica: {e}")
            return []
    
    def get_context_for_query(self, query: str, area: str = None, k: int = 3) -> str:
        """Obtém contexto relevante para uma query"""
        filter_dict = {"area": {"$eq": area}} if area else None
        
        results = self.semantic_search(query, k=k, filter_dict=filter_dict)
        
        if not results:
            return "Nenhum equipamento relevante encontrado."
        
        context_parts = ["Equipamentos relevantes encontrados:\n"]
        for i, result in enumerate(results, 1):
            context_parts.append(f"\n{i}. {result['content']}")
        
        return "\n".join(context_parts)

rag_service = RAGService()
