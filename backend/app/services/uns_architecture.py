from typing import Dict, List, Any, Optional
from app.models.schemas import Equipment
from app.services.google_sheets import sheets_service
from collections import defaultdict
import json

class UNSArchitectureService:
    """Serviço para gerar arquitetura UNS hierárquica"""
    
    def __init__(self):
        self.hierarchy_levels = [
            'empresa',
            'planta', 
            'area',
            'ute',
            'linha',
            'estacao',
            'maquina',
            'equipamento'
        ]
    
    def build_uns_tree(self, equipments: List[Equipment]) -> Dict[str, Any]:
        """Constrói árvore UNS completa"""
        
        tree = {
            "name": "Planta Industrial",
            "type": "empresa",
            "children": {}
        }
        
        for equipment in equipments:
            self._add_equipment_to_tree(tree, equipment)
        
        tree_formatted = self._format_tree(tree)
        
        return tree_formatted
    
    def _add_equipment_to_tree(self, tree: Dict, equipment: Equipment):
        """Adiciona equipamento à árvore UNS"""
        
        current = tree
        
        # Nível: Área
        if equipment.area:
            if 'children' not in current:
                current['children'] = {}
            
            area_key = self._normalize_key(equipment.area)
            if area_key not in current['children']:
                current['children'][area_key] = {
                    "name": equipment.area,
                    "type": "area",
                    "children": {}
                }
            current = current['children'][area_key]
        
        # Nível: UTE
        if equipment.ute:
            if 'children' not in current:
                current['children'] = {}
            
            ute_key = self._normalize_key(equipment.ute)
            if ute_key not in current['children']:
                current['children'][ute_key] = {
                    "name": equipment.ute,
                    "type": "ute",
                    "children": {}
                }
            current = current['children'][ute_key]
        
        # Nível: Linha
        if equipment.linha:
            if 'children' not in current:
                current['children'] = {}
            
            linha_key = self._normalize_key(equipment.linha)
            if linha_key not in current['children']:
                current['children'][linha_key] = {
                    "name": equipment.linha,
                    "type": "linha",
                    "children": {}
                }
            current = current['children'][linha_key]
        
        # Nível: Estação
        if equipment.estacao:
            if 'children' not in current:
                current['children'] = {}
            
            estacao_key = self._normalize_key(equipment.estacao)
            if estacao_key not in current['children']:
                current['children'][estacao_key] = {
                    "name": equipment.estacao,
                    "type": "estacao",
                    "children": {}
                }
            current = current['children'][estacao_key]
        
        # Nível: Máquina/Equipamento
        if equipment.codigo:
            if 'children' not in current:
                current['children'] = {}
            
            equip_key = self._normalize_key(equipment.codigo)
            current['children'][equip_key] = {
                "name": equipment.descricao or equipment.codigo,
                "type": "equipamento",
                "codigo": equipment.codigo,
                "descricao": equipment.descricao,
                "maquina": equipment.maquina,
                "metadata": {
                    "area": equipment.area,
                    "ute": equipment.ute,
                    "linha": equipment.linha,
                    "estacao": equipment.estacao,
                    "tipo": equipment.tipo
                }
            }
    
    def _normalize_key(self, text: str) -> str:
        """Normaliza texto para usar como chave"""
        if not text:
            return "undefined"
        
        import re
        key = re.sub(r'[^a-zA-Z0-9_-]', '_', text)
        key = re.sub(r'_+', '_', key)
        return key.lower().strip('_')
    
    def _format_tree(self, node: Dict) -> Dict:
        """Formata árvore convertendo dicts em listas"""
        formatted = {
            "name": node.get("name", "Root"),
            "type": node.get("type", "root"),
        }
        
        if "codigo" in node:
            formatted["codigo"] = node["codigo"]
        if "descricao" in node:
            formatted["descricao"] = node["descricao"]
        if "metadata" in node:
            formatted["metadata"] = node["metadata"]
        
        if "children" in node and node["children"]:
            formatted["children"] = [
                self._format_tree(child) 
                for child in node["children"].values()
            ]
        
        return formatted
    
    def generate_markdown_hierarchy(self, equipments: List[Equipment], max_items: int = 100) -> str:
        """Gera representação em MARKDOWN FORMATADO da hierarquia UNS"""
        
        tree = self.build_uns_tree(equipments)
        
        lines = []
        lines.append("# 🏭 ARQUITETURA UNS - UNIFIED NAMESPACE\n")
        lines.append("**Unified Namespace** é a estrutura hierárquica que organiza todos os dados industriais.\n")
        
        # Estatísticas resumidas
        stats = self.get_statistics(equipments)
        lines.append("## 📊 Visão Geral\n")
        lines.append(f"- **Total de Equipamentos:** {stats['total_equipments']}")
        lines.append(f"- **Profundidade da Hierarquia:** {stats['depth']} níveis")
        lines.append(f"- **Áreas Mapeadas:** {len(stats['by_area'])}\n")
        
        lines.append("---\n")
        lines.append("## 🗂️ Estrutura Hierárquica\n")
        
        item_count = [0]  # Contador de itens
        self._append_markdown_tree(tree, lines, 0, item_count, max_items)
        
        if item_count[0] >= max_items:
            lines.append(f"\n*... e mais {stats['total_equipments'] - max_items} equipamentos não exibidos*")
        
        lines.append("\n---\n")
        lines.append("### 📝 Legenda dos Níveis:\n")
        lines.append("- 🏢 **Empresa** - Nível raiz da organização")
        lines.append("- 🏗️ **Área** - Áreas de produção (GENERAL SERVICES, FUNILARIA, PINTURA, etc)")
        lines.append("- ⚡ **UTE** - Unidades de Tratamento Especial")
        lines.append("- 🔧 **Linha** - Linhas de produção")
        lines.append("- 🔩 **Estação** - Estações de trabalho")
        lines.append("- 📦 **Equipamento** - Equipamentos e máquinas individuais")
        
        return "\n".join(lines)
    
    def _append_markdown_tree(self, node: Dict, lines: List[str], level: int, 
                              item_count: List[int], max_items: int):
        """Adiciona nó à representação em Markdown com formatação rica"""
        
        if item_count[0] >= max_items:
            return
        
        item_count[0] += 1
        
        indent = "  " * level
        icon = self._get_icon(node.get("type", ""))
        
        name = node.get("name", "Unknown")
        node_type = node.get("type", "")
        
        # Formatação diferente por tipo
        if node_type == "empresa":
            lines.append(f"### {icon} **{name}**\n")
        elif node_type == "area":
            lines.append(f"{indent}#### {icon} **{name}**")
        elif node_type == "ute":
            lines.append(f"{indent}##### {icon} *{name}*")
        elif node_type == "linha":
            lines.append(f"{indent}- {icon} **Linha:** {name}")
        elif node_type == "estacao":
            lines.append(f"{indent}  - {icon} **Estação:** {name}")
        elif node_type == "equipamento":
            codigo = node.get("codigo", "N/A")
            lines.append(f"{indent}    - {icon} `{codigo}` - {name}")
        else:
            lines.append(f"{indent}- {icon} {name}")
        
        # Processa filhos
        if "children" in node:
            for child in node["children"]:
                if item_count[0] >= max_items:
                    break
                self._append_markdown_tree(child, lines, level + 1, item_count, max_items)
    
    def _get_icon(self, node_type: str) -> str:
        """Retorna ícone baseado no tipo de nó"""
        icons = {
            "empresa": "��",
            "planta": "🏭",
            "area": "🏗️",
            "ute": "⚡",
            "linha": "🔧",
            "estacao": "🔩",
            "maquina": "⚙️",
            "equipamento": "📦"
        }
        return icons.get(node_type.lower(), "•")
    
    def generate_summary_by_area(self, equipments: List[Equipment]) -> str:
        """Gera resumo organizado por área em Markdown"""
        
        lines = []
        lines.append("# 📊 RESUMO POR ÁREA - UNS\n")
        
        # Agrupa por área
        by_area = defaultdict(list)
        for eq in equipments:
            if eq.area:
                by_area[eq.area].append(eq)
        
        # Para cada área
        for area, area_equipments in sorted(by_area.items()):
            lines.append(f"## 🏗️ {area}\n")
            lines.append(f"**Total de equipamentos:** {len(area_equipments)}\n")
            
            # Agrupa por UTE
            by_ute = defaultdict(list)
            for eq in area_equipments:
                ute = eq.ute or "Sem UTE"
                by_ute[ute].append(eq)
            
            for ute, ute_equipments in sorted(by_ute.items()):
                lines.append(f"### ⚡ {ute}")
                lines.append(f"*{len(ute_equipments)} equipamento(s)*\n")
                
                # Agrupa por linha
                by_linha = defaultdict(list)
                for eq in ute_equipments:
                    linha = eq.linha or "Sem Linha"
                    by_linha[linha].append(eq)
                
                for linha, linha_equipments in sorted(by_linha.items()):
                    lines.append(f"- 🔧 **{linha}** ({len(linha_equipments)} equipamentos)")
                    
                    # Lista até 5 equipamentos
                    for eq in linha_equipments[:5]:
                        if eq.codigo and eq.descricao:
                            lines.append(f"  - 📦 `{eq.codigo}` {eq.descricao}")
                    
                    if len(linha_equipments) > 5:
                        lines.append(f"  - *... e mais {len(linha_equipments) - 5} equipamentos*")
                
                lines.append("")
            
            lines.append("---\n")
        
        return "\n".join(lines)
    
    def get_statistics(self, equipments: List[Equipment]) -> Dict[str, Any]:
        """Gera estatísticas da arquitetura"""
        
        stats = {
            "total_equipments": len(equipments),
            "by_level": defaultdict(int),
            "by_area": defaultdict(int),
            "by_ute": defaultdict(int),
            "by_linha": defaultdict(int),
            "depth": 0
        }
        
        for eq in equipments:
            if eq.area:
                stats["by_area"][eq.area] += 1
                stats["by_level"]["area"] += 1
            
            if eq.ute:
                stats["by_ute"][eq.ute] += 1
                stats["by_level"]["ute"] += 1
            
            if eq.linha:
                stats["by_linha"][eq.linha] += 1
                stats["by_level"]["linha"] += 1
            
            # Calcula profundidade
            depth = 1
            if eq.area: depth += 1
            if eq.ute: depth += 1
            if eq.linha: depth += 1
            if eq.estacao: depth += 1
            
            stats["depth"] = max(stats["depth"], depth)
        
        # Converte defaultdict para dict normal
        stats["by_area"] = dict(stats["by_area"])
        stats["by_ute"] = dict(stats["by_ute"])
        stats["by_linha"] = dict(stats["by_linha"])
        stats["by_level"] = dict(stats["by_level"])
        
        return stats

# Singleton
uns_architecture_service = UNSArchitectureService()
