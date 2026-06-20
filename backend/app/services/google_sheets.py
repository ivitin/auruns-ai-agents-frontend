import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any, Optional
import pandas as pd
import time
from app.config.settings import settings
from app.models.schemas import Equipment

CACHE_TTL_SECONDS = 300  # 5 minutos

class GoogleSheetsService:
    """Serviço para gerenciar acesso ao Google Sheets"""

    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        self.client = None
        self.spreadsheet = None
        self._cache: Optional[List[Equipment]] = None
        self._cache_at: float = 0.0
        self._areas_cache: Optional[List[str]] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa o cliente do Google Sheets"""
        try:
            creds = Credentials.from_service_account_file(
                settings.GOOGLE_SHEETS_CREDENTIALS_FILE,
                scopes=self.scopes
            )
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(settings.GOOGLE_SHEET_ID)
            print("✅ Google Sheets conectado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao conectar com Google Sheets: {e}")
            raise
    
    def _normalize_columns(self, df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
        """Normaliza colunas com base na área"""
        column_mapping = {
            'Nivel': 'nivel', 'Local': 'local', 'Localização': 'localizacao',
            'UTE': 'ute', 'Linha': 'linha', 'Operação': 'operacao',
            'Operacao': 'operacao', 'Estacao': 'estacao', 'Estação': 'estacao',
            'Maquina': 'maquina', 'Máquina': 'maquina', 'Equipamento': 'equipamento',
            'Codigo': 'codigo', 'Código': 'codigo', 'Descricao': 'descricao',
            'Descrição': 'descricao', 'DescricaoMaquina': 'descricao',
            'Denominação do objeto técnico': 'denominacao', 'Outro': 'tipo',
        }
        
        df = df.rename(columns=column_mapping)
        df['area'] = sheet_name.upper()
        return df
    
    def get_sheet_data(self, sheet_name: str) -> List[Dict[str, Any]]:
        """Obtém dados de uma planilha específica"""
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            df = self._normalize_columns(df, sheet_name)
            df = df.dropna(how='all')
            return df.to_dict('records')
        except Exception as e:
            print(f"❌ Erro ao ler planilha {sheet_name}: {e}")
            return []
    
    def get_available_areas(self) -> List[str]:
        """Detecta dinamicamente quais abas existem na planilha"""
        if self._areas_cache:
            return self._areas_cache

        known_areas = ["GENERAL SERVICES", "FUNILARIA", "PINTURA", "MONTAGEM", "PRENSAS"]
        try:
            existing = {ws.title for ws in self.spreadsheet.worksheets()}
            self._areas_cache = [a for a in known_areas if a in existing]
            print(f"✅ Áreas detectadas: {self._areas_cache}")
        except Exception as e:
            print(f"⚠️ Erro ao detectar áreas, usando lista completa: {e}")
            self._areas_cache = known_areas

        return self._areas_cache

    def invalidate_cache(self):
        """Invalida o cache forçando recarga na próxima chamada"""
        self._cache = None
        self._cache_at = 0.0
        self._areas_cache = None
        print("🔄 Cache do Sheets invalidado")

    def get_all_equipments(self, force_refresh: bool = False) -> List[Equipment]:
        """Obtém todos os equipamentos com cache de 5 minutos"""
        now = time.time()
        if not force_refresh and self._cache is not None and (now - self._cache_at) < CACHE_TTL_SECONDS:
            return self._cache

        areas = self.get_available_areas()
        all_equipments = []

        for area in areas:
            try:
                data = self.get_sheet_data(area)
                for item in data:
                    try:
                        equipment = Equipment(**item)
                        all_equipments.append(equipment)
                    except Exception:
                        continue
                print(f"✅ {len(data)} equipamentos carregados de {area}")
            except Exception as e:
                print(f"❌ Erro ao processar área {area}: {e}")
                continue

        self._cache = all_equipments
        self._cache_at = now
        print(f"✅ Total de {len(all_equipments)} equipamentos carregados (cache atualizado)!")
        return all_equipments

sheets_service = GoogleSheetsService()
