import re
from typing import List, Set, Dict
from unidecode import unidecode

EQUIPMENT_TYPE_KEYWORDS: Dict[str, List[str]] = {
    "robo": ["robô", "robo", "robot", "krc", "kuka", "fanuc", "abb", "yaskawa", "manipulad"],
    "prensa": ["prensa", "schuler", "press"],
    "elevador": ["elevador", "elev", "lift"],
    "bomba": ["bomba", "pump"],
    "chiller": ["chiller", "resfriamento"],
    "ponte_rolante": ["ponte rolante", "guindaste", "pórtico"],
    "mesa": ["mesa", "bancada", "workstation"],
}


def classify_equipment_type(descricao: str = "", maquina: str = "", denominacao: str = "") -> str:
    """Classifica o tipo de equipamento por keywords na descrição"""
    text = " ".join(filter(None, [descricao, maquina, denominacao])).lower()
    for tipo, keywords in EQUIPMENT_TYPE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return tipo
    return "outro"

class NLPUtils:
    """Classe com utilitários de NLP"""
    
    STOPWORDS_PT = {
        'a', 'o', 'e', 'de', 'da', 'do', 'em', 'um', 'uma', 'os', 'as',
        'dos', 'das', 'para', 'com', 'por', 'que', 'se', 'na', 'no',
        'ao', 'aos', 'à', 'às', 'pelo', 'pela', 'pelos', 'pelas'
    }
    
    INDUSTRIAL_TERMS = {
        'bomba', 'chiller', 'robo', 'robô', 'prensa', 'elevador',
        'ponte', 'rolante', 'motor', 'desbobinamento', 'empilhamento',
        'sigilatura', 'pintura', 'funilaria', 'montagem', 'ute',
        'linha', 'estacao', 'estação', 'maquina', 'máquina', 'equipamento'
    }
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normaliza texto"""
        if not text:
            return ""
        text = text.lower()
        text = unidecode(text)
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokeniza texto"""
        text = NLPUtils.normalize_text(text)
        return text.split()
    
    @staticmethod
    def remove_stopwords(tokens: List[str]) -> List[str]:
        """Remove stopwords"""
        return [token for token in tokens if token not in NLPUtils.STOPWORDS_PT]
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 5) -> List[str]:
        """Extrai palavras-chave"""
        tokens = NLPUtils.tokenize(text)
        tokens = NLPUtils.remove_stopwords(tokens)
        
        industrial_keywords = [t for t in tokens if t in NLPUtils.INDUSTRIAL_TERMS]
        other_keywords = [t for t in tokens if t not in NLPUtils.INDUSTRIAL_TERMS]
        
        keywords = industrial_keywords + other_keywords
        
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
        
        return unique_keywords[:top_n]
    
    @staticmethod
    def identify_area(text: str) -> str:
        """Identifica área mencionada"""
        text_norm = NLPUtils.normalize_text(text)
        
        area_keywords = {
            'GENERAL SERVICES': ['bomba', 'chiller', 'resfriamento', 'agua'],
            'FUNILARIA': ['funilaria', 'auc'],
            'PINTURA': ['pintura', 'ubs', 'sigilatura'],
            'MONTAGEM': ['montagem', 'elevador', 'pbs'],
            'PRENSAS': ['prensa', 'schuler', 'desbobinamento']
        }
        
        area_scores = {}
        for area, keywords in area_keywords.items():
            score = sum(1 for kw in keywords if kw in text_norm)
            if score > 0:
                area_scores[area] = score
        
        if not area_scores:
            return None
        
        return max(area_scores, key=area_scores.get)
