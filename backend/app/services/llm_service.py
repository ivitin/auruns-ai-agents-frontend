from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from app.config.settings import settings
from typing import List, Dict, Any
import json

class LLMService:
    """Serviço para gerenciar interações com LLM"""
    
    def should_generate_architecture(self, user_input: str) -> bool:
        """Detecta se usuário quer ver arquitetura UNS"""
        triggers = [
            'arquitetura', 'estrutura', 'hierarquia', 'organização',
            'gerar uns', 'mostrar uns', 'estrutura uns', 'topologia',
            'mapa', 'organograma', 'árvore'
        ]
        user_lower = user_input.lower()
        return any(trigger in user_lower for trigger in triggers)


    def __init__(self):
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Inicializa o modelo LLM"""
        try:
            # Usa Groq (gratuito e rápido)
            if settings.GROQ_API_KEY:
                self.llm = ChatGroq(
                    groq_api_key=settings.GROQ_API_KEY,
                    model_name=settings.GROQ_MODEL_NAME,
                    temperature=settings.TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS,
                )
                print(f"✅ LLM Groq ({settings.GROQ_MODEL_NAME}) inicializado!")
            else:
                raise Exception("GROQ_API_KEY não configurada")
                
        except Exception as e:
            print(f"❌ Erro ao inicializar LLM: {e}")
            raise
    
    def create_uns_agent_prompt(self) -> ChatPromptTemplate:
        """Cria o prompt template para o agente UNS"""
        system_template = """Você é um assistente especializado em Indústria 4.0 e UNS (Unified Namespace).
Seu papel é ajudar usuários a encontrar e entender informações sobre equipamentos industriais.

**Sobre UNS:**
- UNS é uma arquitetura de dados centralizada para Indústria 4.0
- Organiza dados hierarquicamente: Empresa > Área > Linha > Célula > Equipamento
- Facilita integração e acesso a dados industriais em tempo real

**Áreas disponíveis:**
- GENERAL SERVICES: Bombas, chillers, sistemas de resfriamento
- FUNILARIA: Robôs de funilaria e processamento de chapas
- PINTURA: Robôs de pintura, UBS, sigilatura
- MONTAGEM: Elevadores, pontes rolantes, sistemas de montagem
- PRENSAS: Prensas Schuler, desbobinamento, empilhamento

**Diretrizes OBRIGATÓRIAS — siga à risca:**
1. Use EXCLUSIVAMENTE os dados do contexto abaixo. PROIBIDO inventar equipamentos.
2. Códigos reais nesta planta seguem o padrão M09XXXXXX (ex: M09200123). Se você ver um código como "B-001" ou "E-001" que NÃO está no contexto, você está inventando — PARE.
3. Se o contexto contiver "Nenhum equipamento encontrado", responda exatamente: "Não encontrei equipamentos com esse critério na base de dados." Não invente alternativas.
4. Quando o contexto listar equipamentos, **liste TODOS** — não omita nenhum do contexto. Use listas markdown.
5. Para cada equipamento inclua: código exato do contexto, descrição e localização (UTE/Linha/Estação).
6. Se o usuário selecionou ativos como contexto (seção "Ativos selecionados"), essas são as máquinas foco da pergunta — responda sobre elas especificamente.
7. Responda SEMPRE em português brasileiro com formatação markdown.

**Contexto dos equipamentos encontrados (use SOMENTE estes dados):**
{context}"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
        ])
        
        return prompt
    
    def generate_response(
        self, 
        user_input: str, 
        context: str = "", 
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """Gera resposta usando o LLM"""
        try:
            prompt = self.create_uns_agent_prompt()
            
            # Prepara histórico
            history_messages = []
            if chat_history:
                for msg in chat_history[-5:]:  # Últimas 5 mensagens
                    if msg["role"] == "user":
                        history_messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        history_messages.append(AIMessage(content=msg["content"]))
            
            # Cria chain
            chain = prompt | self.llm | StrOutputParser()
            
            # Gera resposta
            response = chain.invoke({
                "input": user_input,
                "context": context,
                "chat_history": history_messages
            })
            
            return response.strip()
            
        except Exception as e:
            print(f"❌ Erro ao gerar resposta: {e}")
            return f"Desculpe, ocorreu um erro ao processar sua solicitação: {str(e)}"
    
    def extract_intent(self, user_input: str) -> Dict[str, Any]:
        """Extrai a intenção do usuário usando LLM"""
        intent_prompt = f"""Analise a seguinte pergunta sobre equipamentos industriais e retorne um JSON com:
1. "tipo": tipo de consulta - pode ser: "busca_equipamento", "informacao_geral", "navegacao_uns", "estatistica"
2. "area": área mencionada - pode ser: "GENERAL SERVICES", "FUNILARIA", "PINTURA", "MONTAGEM", "PRENSAS" ou null
3. "termos": lista de termos-chave relevantes extraídos da pergunta

Pergunta: {user_input}

Responda APENAS com JSON válido, sem texto adicional:"""

        try:
            response = self.llm.invoke([
                SystemMessage(content="Você é um analisador de intenções. Retorne APENAS JSON válido."),
                HumanMessage(content=intent_prompt)
            ])
            
            # Extrai JSON da resposta
            content = response.content.strip()
            
            # Remove markdown code blocks se houver
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            # Parse JSON
            intent = json.loads(content)
            
            return intent
            
        except Exception as e:
            print(f"⚠️ Erro ao extrair intent com LLM: {e}")
            # Fallback simples
            user_lower = user_input.lower()
            
            area = None
            if 'bomba' in user_lower or 'chiller' in user_lower:
                area = 'GENERAL SERVICES'
            elif 'funilaria' in user_lower:
                area = 'FUNILARIA'
            elif 'pintura' in user_lower:
                area = 'PINTURA'
            elif 'montagem' in user_lower or 'elevador' in user_lower:
                area = 'MONTAGEM'
            elif 'prensa' in user_lower:
                area = 'PRENSAS'
            
            return {
                "tipo": "busca_equipamento",
                "area": area,
                "termos": user_input.split()[:5],
                "filtros": {}
            }

llm_service = LLMService()
