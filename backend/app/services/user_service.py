import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json
from app.config.settings import settings
from app.models.schemas import User, Interaction

class UserService:
    """Serviço para gerenciar usuários e interações"""
    
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.client = None
        self.spreadsheet = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa cliente Google Sheets"""
        try:
            creds = Credentials.from_service_account_file(
                settings.GOOGLE_SHEETS_CREDENTIALS_FILE,
                scopes=self.scopes
            )
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(settings.GOOGLE_SHEET_ID)
            print("✅ UserService: Google Sheets conectado!")
        except Exception as e:
            print(f"❌ Erro ao conectar UserService: {e}")
            raise
    
    def get_or_create_user(self, username: str, email: Optional[str] = None) -> User:
        """Obtém usuário existente ou cria novo"""
        try:
            # Tenta obter worksheet Users
            try:
                users_sheet = self.spreadsheet.worksheet("Users")
            except:
                # Cria worksheet se não existir
                users_sheet = self.spreadsheet.add_worksheet(
                    title="Users",
                    rows=1000,
                    cols=6
                )
                # Adiciona headers
                users_sheet.append_row([
                    "user_id", "username", "email", "created_at", "last_login", "role"
                ])
            
            # Busca usuário existente
            all_users = users_sheet.get_all_records()
            for user_data in all_users:
                if user_data['username'] == username:
                    # Atualiza last_login
                    user = User(**user_data)
                    user.last_login = datetime.now().isoformat()
                    self._update_user(users_sheet, user)
                    return user
            
            # Cria novo usuário
            new_user = User(
                user_id=str(uuid.uuid4()),
                username=username,
                email=email,
                created_at=datetime.now().isoformat(),
                last_login=datetime.now().isoformat(),
                role="user"
            )
            
            users_sheet.append_row([
                new_user.user_id,
                new_user.username,
                new_user.email or "",
                new_user.created_at,
                new_user.last_login,
                new_user.role
            ])
            
            print(f"✅ Novo usuário criado: {username}")
            return new_user
            
        except Exception as e:
            print(f"❌ Erro ao obter/criar usuário: {e}")
            raise
    
    def _update_user(self, sheet, user: User):
        """Atualiza informações do usuário"""
        try:
            all_users = sheet.get_all_records()
            for idx, user_data in enumerate(all_users, start=2):
                if user_data['user_id'] == user.user_id:
                    sheet.update(f'E{idx}', user.last_login)
                    break
        except Exception as e:
            print(f"⚠️ Erro ao atualizar usuário: {e}")
    
    def save_interaction(
        self,
        user_id: str,
        conversation_id: str,
        user_message: str,
        agent_response: str,
        sources: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """Salva interação na planilha"""
        try:
            # Obtém ou cria worksheet Interactions
            try:
                interactions_sheet = self.spreadsheet.worksheet("Interactions")
            except:
                interactions_sheet = self.spreadsheet.add_worksheet(
                    title="Interactions",
                    rows=10000,
                    cols=9
                )
                interactions_sheet.append_row([
                    "interaction_id", "user_id", "conversation_id", "timestamp",
                    "user_message", "agent_response", "sources", "feedback", "metadata"
                ])
            
            interaction_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            interactions_sheet.append_row([
                interaction_id,
                user_id,
                conversation_id,
                timestamp,
                user_message,
                agent_response,
                json.dumps(sources) if sources else "",
                "",
                json.dumps(metadata) if metadata else ""
            ])
            
            return interaction_id
            
        except Exception as e:
            print(f"❌ Erro ao salvar interação: {e}")
            return ""
    
    def update_interaction_feedback(
        self,
        interaction_id: str,
        feedback: str,
        comment: Optional[str] = None
    ):
        """Atualiza feedback de uma interação"""
        try:
            interactions_sheet = self.spreadsheet.worksheet("Interactions")
            all_interactions = interactions_sheet.get_all_records()
            
            for idx, interaction in enumerate(all_interactions, start=2):
                if interaction['interaction_id'] == interaction_id:
                    feedback_data = {
                        "type": feedback,
                        "comment": comment,
                        "timestamp": datetime.now().isoformat()
                    }
                    interactions_sheet.update(f'H{idx}', [[json.dumps(feedback_data)]])
                    print(f"✅ Feedback atualizado: {interaction_id}")
                    break
                    
        except Exception as e:
            print(f"❌ Erro ao atualizar feedback: {e}")   
    def get_user_context(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Obtém contexto do usuário baseado em histórico"""
        try:
            interactions_sheet = self.spreadsheet.worksheet("Interactions")
            all_interactions = interactions_sheet.get_all_records()
            
            user_interactions = [
                i for i in all_interactions 
                if i['user_id'] == user_id
            ]
            
            user_interactions.sort(
                key=lambda x: x['timestamp'],
                reverse=True
            )
            
            recent = user_interactions[:limit]
            
            topics = {}
            for interaction in recent:
                msg = interaction['user_message'].lower()
                keywords = ['bomba', 'robô', 'prensa', 'elevador', 'uns', 'arquitetura']
                for keyword in keywords:
                    if keyword in msg:
                        topics[keyword] = topics.get(keyword, 0) + 1
            
            common_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
            common_topics = [t[0] for t in common_topics[:5]]
            
            return {
                "user_id": user_id,
                "recent_interactions": recent,
                "common_topics": common_topics,
                "total_interactions": len(user_interactions),
                "preferences": {
                    "most_queried_topics": common_topics
                }
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter contexto do usuário: {e}")
            return {
                "user_id": user_id,
                "recent_interactions": [],
                "common_topics": [],
                "total_interactions": 0,
                "preferences": {}
            }
    
    def get_user_history_summary(self, user_id: str) -> str:
        """Gera resumo textual do histórico do usuário para o LLM"""
        context = self.get_user_context(user_id, limit=5)
        
        if context['total_interactions'] == 0:
            return "Este é um novo usuário sem histórico de interações."
        
        summary_parts = []
        summary_parts.append(f"Histórico do usuário ({context['total_interactions']} interações totais):")
        
        if context['common_topics']:
            summary_parts.append(f"Tópicos de interesse: {', '.join(context['common_topics'])}")
        
        if context['recent_interactions']:
            summary_parts.append("\nÚltimas interações:")
            for i, interaction in enumerate(context['recent_interactions'][:3], 1):
                summary_parts.append(f"{i}. Perguntou sobre: {interaction['user_message'][:100]}")
        
        return "\n".join(summary_parts)

# Singleton
user_service = UserService()
