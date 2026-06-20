from fastapi import APIRouter, HTTPException
from typing import Dict
from app.models.schemas import ChatRequest, ChatResponse, EquipmentQuery, EquipmentQueryResponse
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.services.google_sheets import sheets_service
from app.services.user_service import user_service
from app.utils.nlp_utils import classify_equipment_type, EQUIPMENT_TYPE_KEYWORDS
import uuid

router = APIRouter(prefix="/chat", tags=["chat"])

conversations: Dict[str, list] = {}


def _extract_tipo_from_message(message: str) -> str:
    """Extrai tipo de equipamento diretamente da mensagem do usuário."""
    msg_lower = message.lower()
    for tipo, keywords in EQUIPMENT_TYPE_KEYWORDS.items():
        if any(kw in msg_lower for kw in keywords):
            return tipo
    return None


def _build_direct_context(equipments, area: str = None, tipo: str = None) -> str:
    """Monta contexto com dados reais do Sheets — sem RAG, sem alucinação."""
    filtered = equipments

    if area:
        filtered = [eq for eq in filtered if (eq.area or "").upper() == area.upper()]

    if tipo:
        filtered = [eq for eq in filtered if _classify_equipment_type(eq) == tipo]

    if not filtered:
        return f"Nenhum equipamento encontrado (área={area or 'todas'}, tipo={tipo or 'todos'})."

    lines = [f"Base de dados — {len(filtered)} equipamento(s) encontrado(s):"]
    for eq in filtered[:60]:
        descr = eq.descricao or eq.maquina or eq.denominacao or ""
        local = " / ".join(filter(None, [eq.ute, eq.linha, eq.estacao]))
        lines.append(
            f"• {eq.codigo or 'S/COD'} | {descr} | Área: {eq.area or '?'}"
            + (f" | Local: {local}" if local else "")
        )

    if len(filtered) > 60:
        lines.append(f"(⚠️ exibindo 60 de {len(filtered)} — refine com mais filtros)")

    return "\n".join(lines)

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Envia mensagem para o agente"""
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # IMPORTANTE: Obtém user_id do contexto
        user_id = request.context.get('user_id', 'anonymous') if request.context else 'anonymous'
        
        print(f"📝 [1/6] Processando mensagem do usuário: {user_id}")

        # Carrega contexto do usuário
        user_context_summary = ""
        if user_id != 'anonymous':
            user_context_summary = user_service.get_user_history_summary(user_id)
        print(f"✔️  [2/6] Contexto do usuário carregado ({len(user_context_summary)} chars)")

        if conversation_id not in conversations:
            conversations[conversation_id] = []

        chat_history = conversations[conversation_id]

        intent = llm_service.extract_intent(request.message)
        print(f"✔️  [3/6] Intent extraído: {intent}")

        explicit_area = request.context.get('area') if request.context else None
        effective_area = explicit_area or intent.get("area")
        selected_assets = request.context.get('selected_assets', []) if request.context else []
        effective_tipo = _extract_tipo_from_message(request.message)

        # Contexto direto do Sheets quando há área ou tipo — evita alucinação
        if effective_area or effective_tipo:
            all_eq = sheets_service.get_all_equipments()
            context = _build_direct_context(all_eq, area=effective_area, tipo=effective_tipo)
            print(f"✔️  [4/6] Contexto DIRETO ({len(context)} chars) area={effective_area} tipo={effective_tipo}")
        else:
            context = rag_service.get_context_for_query(request.message, area=None, k=10)
            print(f"✔️  [4/6] RAG context ({len(context)} chars)")

        assets_context = ""
        if selected_assets:
            lines = [
                f"- {a.get('codigo','N/A')}: {a.get('descricao') or a.get('maquina','')} "
                f"({a.get('area','')} / {a.get('ute','')} / {a.get('linha','')})"
                for a in selected_assets
            ]
            assets_context = "Ativos selecionados pelo usuário como foco da pergunta:\n" + "\n".join(lines) + "\n\n"

        full_context = f"{assets_context}{user_context_summary}\n\n{context}"

        print(f"✔️  [5/6] Gerando resposta LLM (context={len(full_context)} chars)...")
        response_text = llm_service.generate_response(
            user_input=request.message,
            context=full_context,
            chat_history=chat_history
        )
        print(f"✔️  [6/6] Resposta LLM gerada ({len(response_text)} chars)")

        chat_history.append({"role": "user", "content": request.message})
        chat_history.append({"role": "assistant", "content": response_text})
        conversations[conversation_id] = chat_history[-10:]

        area_filter = {"area": {"$eq": effective_area}} if effective_area else None
        sources = rag_service.semantic_search(
            request.message,
            k=3,
            filter_dict=area_filter
        )
        
        # SALVA INTERAÇÃO
        interaction_id = ""
        if user_id != 'anonymous':
            interaction_id = user_service.save_interaction(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message=request.message,
                agent_response=response_text,
                sources=sources,
                metadata={"intent": intent}
            )
            print(f"✅ Interação salva: {interaction_id}")
        else:
            print("⚠️ Usuário anônimo, interação não salva")
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            sources=sources,
            metadata={
                "intent": intent,
                "interaction_id": interaction_id,
                "user_id": user_id
            }
        )
        
    except Exception as e:
        print(f"❌ Erro ao processar mensagem: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Recupera histórico"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id]
    }

@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Deleta conversa"""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": "Conversa deletada"}
    raise HTTPException(status_code=404, detail="Conversa não encontrada")

@router.post("/query-equipments", response_model=EquipmentQueryResponse)
async def query_equipments(query: EquipmentQuery):
    """Busca equipamentos"""
    try:
        intent = llm_service.extract_intent(query.query)
        
        results = rag_service.semantic_search(
            query.query,
            k=query.limit,
            filter_dict=query.filters if query.filters else None
        )
        
        all_equipments = sheets_service.get_all_equipments()
        
        matched_equipments = []
        for result in results:
            codigo = result['metadata'].get('codigo')
            if codigo:
                for eq in all_equipments:
                    if eq.codigo == codigo:
                        matched_equipments.append(eq)
                        break
        
        interpretation = f"Encontrados {len(matched_equipments)} equipamentos: {query.query}"
        if intent.get('area'):
            interpretation += f" na área {intent['area']}"
        
        return EquipmentQueryResponse(
            equipments=matched_equipments[:query.limit],
            total=len(matched_equipments),
            query=query.query,
            interpretation=interpretation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/areas")
async def get_areas():
    """Lista áreas disponíveis detectadas dinamicamente nas planilhas"""
    return {"areas": sheets_service.get_available_areas()}

def _classify_equipment_type(equipment) -> str:
    return classify_equipment_type(
        descricao=equipment.descricao or "",
        maquina=equipment.maquina or "",
        denominacao=equipment.denominacao or "",
    )


@router.get("/stats")
async def get_statistics():
    """Estatísticas com contagem por área e por tipo de ativo"""
    try:
        equipments = sheets_service.get_all_equipments()

        stats = {
            "total_equipments": len(equipments),
            "by_area": {},
            "by_ute": {},
            "by_type": {},
            "robots_by_area": {},
            "by_type_and_area": {},
        }

        for eq in equipments:
            area = eq.area or "Unknown"
            stats["by_area"][area] = stats["by_area"].get(area, 0) + 1

            ute = eq.ute or "Unknown"
            stats["by_ute"][ute] = stats["by_ute"].get(ute, 0) + 1

            tipo = _classify_equipment_type(eq)
            stats["by_type"][tipo] = stats["by_type"].get(tipo, 0) + 1

            if tipo == "robo":
                stats["robots_by_area"][area] = stats["robots_by_area"].get(area, 0) + 1

            by_ta = stats["by_type_and_area"]
            if tipo not in by_ta:
                by_ta[tipo] = {}
            by_ta[tipo][area] = by_ta[tipo].get(area, 0) + 1

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/equipment-list")
async def list_equipments(area: str = None, tipo: str = None, limit: int = 100):
    """Lista ativos com filtro por área e/ou tipo (robo, prensa, elevador, bomba, chiller, ponte_rolante, mesa)"""
    try:
        equipments = sheets_service.get_all_equipments()

        if area:
            equipments = [eq for eq in equipments if eq.area == area.upper()]

        if tipo:
            equipments = [eq for eq in equipments if _classify_equipment_type(eq) == tipo.lower()]

        items = [
            {
                "codigo": eq.codigo,
                "descricao": eq.descricao,
                "area": eq.area,
                "ute": eq.ute,
                "linha": eq.linha,
                "estacao": eq.estacao,
                "maquina": eq.maquina,
                "tipo": _classify_equipment_type(eq),
            }
            for eq in equipments[:limit]
        ]

        return {"total": len(equipments), "area": area, "tipo": tipo, "equipments": items}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


from app.services.uns_architecture import uns_architecture_service
from app.models.schemas import UNSArchitectureRequest, UNSArchitectureResponse

@router.post("/generate-architecture", response_model=UNSArchitectureResponse)
async def generate_uns_architecture(request: UNSArchitectureRequest):
    """Gera arquitetura UNS"""
    try:
        equipments = sheets_service.get_all_equipments()
        
        if request.area:
            equipments = [eq for eq in equipments if eq.area == request.area]
        
        if request.format == "json":
            architecture = uns_architecture_service.build_uns_tree(equipments)
        elif request.format == "markdown":
            architecture = uns_architecture_service.generate_markdown_hierarchy(equipments)
        elif request.format == "summary":
            architecture = uns_architecture_service.generate_summary_by_area(equipments)
        else:
            architecture = uns_architecture_service.generate_markdown_hierarchy(equipments)
        
        statistics = uns_architecture_service.get_statistics(equipments)
        
        return UNSArchitectureResponse(
            architecture=architecture,
            statistics=statistics,
            format=request.format
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/architecture-preview")
async def get_architecture_preview():
    """Preview da arquitetura"""
    try:
        equipments = sheets_service.get_all_equipments()
        text_hierarchy = uns_architecture_service.generate_markdown_hierarchy(equipments[:50])
        
        return {
            "preview": text_hierarchy,
            "total_equipments": len(equipments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")
