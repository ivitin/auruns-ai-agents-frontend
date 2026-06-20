from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import defaultdict
import json
from app.services.user_service import user_service

class AnalyticsService:
    """Serviço para análise de métricas do agente"""
    
    def __init__(self):
        pass
    
    def get_overall_metrics(self) -> Dict[str, Any]:
        """Obtém métricas gerais do sistema"""
        try:
            # Carrega dados
            users_sheet = user_service.spreadsheet.worksheet("Users")
            interactions_sheet = user_service.spreadsheet.worksheet("Interactions")
            
            users = users_sheet.get_all_records()
            interactions = interactions_sheet.get_all_records()
            
            # Calcula métricas
            total_users = len(users)
            total_interactions = len(interactions)
            
            # Feedback
            positive_feedback = sum(1 for i in interactions if i.get('feedback') and 'positive' in i['feedback'])
            negative_feedback = sum(1 for i in interactions if i.get('feedback') and 'negative' in i['feedback'])
            feedback_rate = (positive_feedback + negative_feedback) / total_interactions * 100 if total_interactions > 0 else 0
            satisfaction_rate = positive_feedback / (positive_feedback + negative_feedback) * 100 if (positive_feedback + negative_feedback) > 0 else 0
            
            # Usuários ativos
            now = datetime.now()
            last_24h = now - timedelta(hours=24)
            active_users_24h = sum(1 for u in users if u.get('last_login') and datetime.fromisoformat(u['last_login']) > last_24h)
            
            # Interações por usuário
            avg_interactions_per_user = total_interactions / total_users if total_users > 0 else 0
            
            return {
                "total_users": total_users,
                "total_interactions": total_interactions,
                "active_users_24h": active_users_24h,
                "avg_interactions_per_user": round(avg_interactions_per_user, 2),
                "feedback": {
                    "positive": positive_feedback,
                    "negative": negative_feedback,
                    "rate": round(feedback_rate, 2),
                    "satisfaction": round(satisfaction_rate, 2)
                }
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular métricas gerais: {e}")
            return {}
    
    def get_usage_metrics(self) -> Dict[str, Any]:
        """Métricas de uso e padrões"""
        try:
            interactions_sheet = user_service.spreadsheet.worksheet("Interactions")
            interactions = interactions_sheet.get_all_records()
            
            # Agrupa por hora do dia
            hours_distribution = defaultdict(int)
            for interaction in interactions:
                if interaction.get('timestamp'):
                    hour = datetime.fromisoformat(interaction['timestamp']).hour
                    hours_distribution[hour] += 1
            
            # Agrupa por dia da semana
            weekday_distribution = defaultdict(int)
            for interaction in interactions:
                if interaction.get('timestamp'):
                    weekday = datetime.fromisoformat(interaction['timestamp']).strftime('%A')
                    weekday_distribution[weekday] += 1
            
            # Top queries
            query_counter = defaultdict(int)
            for interaction in interactions:
                msg = interaction.get('user_message', '')[:50]  # Primeiras 50 chars
                if msg:
                    query_counter[msg] += 1
            
            top_queries = sorted(query_counter.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "peak_hours": dict(sorted(hours_distribution.items(), key=lambda x: x[1], reverse=True)[:5]),
                "weekday_distribution": dict(weekday_distribution),
                "top_queries": [{"query": q, "count": c} for q, c in top_queries]
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular métricas de uso: {e}")
            return {}
    
    def get_content_metrics(self) -> Dict[str, Any]:
        """Métricas sobre o conteúdo consultado"""
        try:
            interactions_sheet = user_service.spreadsheet.worksheet("Interactions")
            interactions = interactions_sheet.get_all_records()
            
            # Áreas mais consultadas
            area_counter = defaultdict(int)
            
            # Equipamentos mais buscados
            equipment_counter = defaultdict(int)
            
            # Queries sem resultados
            no_results = 0
            
            for interaction in interactions:
                # Extrai metadata
                metadata_str = interaction.get('metadata', '{}')
                try:
                    metadata = json.loads(metadata_str) if metadata_str else {}
                    intent = metadata.get('intent', {})
                    
                    # Conta área
                    area = intent.get('area')
                    if area:
                        area_counter[area] += 1
                    
                except:
                    pass
                
                # Verifica se teve resultados
                sources_str = interaction.get('sources', '')
                if not sources_str or sources_str == '[]':
                    no_results += 1
                else:
                    # Conta equipamentos mencionados nas fontes
                    try:
                        sources = json.loads(sources_str) if sources_str else []
                        for source in sources:
                            codigo = source.get('metadata', {}).get('codigo')
                            if codigo:
                                equipment_counter[codigo] += 1
                    except:
                        pass
            
            # Taxa de sucesso do RAG
            total = len(interactions)
            rag_success_rate = ((total - no_results) / total * 100) if total > 0 else 0
            
            return {
                "top_areas": dict(sorted(area_counter.items(), key=lambda x: x[1], reverse=True)),
                "top_equipments": dict(sorted(equipment_counter.items(), key=lambda x: x[1], reverse=True)[:10]),
                "queries_without_results": no_results,
                "rag_success_rate": round(rag_success_rate, 2)
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular métricas de conteúdo: {e}")
            return {}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Métricas de performance do LLM e sistema"""
        try:
            interactions_sheet = user_service.spreadsheet.worksheet("Interactions")
            interactions = interactions_sheet.get_all_records()
            
            # Análise de intents
            intent_distribution = defaultdict(int)
            
            # Tamanho médio das respostas
            response_lengths = []
            
            for interaction in interactions:
                # Intent
                metadata_str = interaction.get('metadata', '{}')
                try:
                    metadata = json.loads(metadata_str) if metadata_str else {}
                    intent_type = metadata.get('intent', {}).get('tipo', 'unknown')
                    intent_distribution[intent_type] += 1
                except:
                    pass
                
                # Tamanho da resposta
                response = interaction.get('agent_response', '')
                if response:
                    response_lengths.append(len(response))
            
            avg_response_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0
            
            return {
                "intent_distribution": dict(intent_distribution),
                "avg_response_length": round(avg_response_length, 2),
                "total_responses_generated": len(interactions)
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular métricas de performance: {e}")
            return {}
    
    def get_user_engagement_metrics(self) -> Dict[str, Any]:
        """Métricas de engajamento dos usuários"""
        try:
            users_sheet = user_service.spreadsheet.worksheet("Users")
            interactions_sheet = user_service.spreadsheet.worksheet("Interactions")
            
            users = users_sheet.get_all_records()
            interactions = interactions_sheet.get_all_records()
            
            # Distribuição de interações por usuário
            user_interaction_count = defaultdict(int)
            for interaction in interactions:
                user_id = interaction.get('user_id')
                if user_id:
                    user_interaction_count[user_id] += 1
            
            # Categoriza usuários
            power_users = sum(1 for count in user_interaction_count.values() if count >= 10)
            regular_users = sum(1 for count in user_interaction_count.values() if 3 <= count < 10)
            casual_users = sum(1 for count in user_interaction_count.values() if count < 3)
            
            # Taxa de retenção (usuários que voltaram)
            returning_users = sum(1 for count in user_interaction_count.values() if count > 1)
            retention_rate = (returning_users / len(users) * 100) if len(users) > 0 else 0
            
            return {
                "power_users": power_users,
                "regular_users": regular_users,
                "casual_users": casual_users,
                "retention_rate": round(retention_rate, 2),
                "most_active_user": max(user_interaction_count.items(), key=lambda x: x[1])[0] if user_interaction_count else None
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular métricas de engajamento: {e}")
            return {}
    
    def generate_full_report(self) -> Dict[str, Any]:
        """Gera relatório completo de analytics"""
        return {
            "generated_at": datetime.now().isoformat(),
            "overall": self.get_overall_metrics(),
            "usage": self.get_usage_metrics(),
            "content": self.get_content_metrics(),
            "performance": self.get_performance_metrics(),
            "engagement": self.get_user_engagement_metrics()
        }

# Singleton
analytics_service = AnalyticsService()
