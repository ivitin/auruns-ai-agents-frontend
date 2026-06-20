"""
test_judge_extended.py

Bateria estendida de testes para LLM Judge
Testa com 15-20 queries para estatística robusta
"""

import sys
import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

# Adicionar o diretório app ao path
sys.path.insert(0, os.path.abspath('.'))

from app.evaluation.llm_judge import LLMJudge

def run_extended_tests():
    """Bateria estendida com 20 casos de teste"""
    print("🚀 Iniciando bateria estendida de testes LLM Judge")
    print("📊 Total de casos: 20 queries\n")

    judge = LLMJudge()

    # Bateria de 20 casos de teste variados
    test_cases = [
        # ===== FUNILARIA (5 casos) =====
        {
            "query": "Quais são os robôs de solda na funilaria?",
            "context": "Área: FUNILARIA | UTE: Body Shop Line 1 | Código: M09400123 | Descrição: Robô de solda 6 eixos para painéis laterais",
            "response": "Na área de funilaria, especificamente na Body Shop Line 1, temos o robô de solda código M09400123. Este é um robô de 6 eixos utilizado para soldagem de painéis laterais."
        },
        {
            "query": "Mostre equipamentos de prensa na funilaria",
            "context": "Área: FUNILARIA | UTE: Press Shop | Código: M09401567 | Descrição: Prensa hidráulica 500 toneladas",
            "response": "Encontrei a prensa hidráulica M09401567 de 500 toneladas no Press Shop da funilaria."
        },
        {
            "query": "Qual o sistema de transporte da funilaria?",
            "context": "Área: FUNILARIA | UTE: Body Shop Line 2 | Código: M09402890 | Descrição: Sistema de transporte por AGV automatizado",
            "response": "O sistema de transporte é o AGV automatizado, código M09402890, localizado na Body Shop Line 2."
        },
        {
            "query": "Tem robô de manipulação de peças?",
            "context": "Área: FUNILARIA | UTE: Parts Handling | Código: M09403124 | Descrição: Robô manipulador KUKA 6 eixos",
            "response": "Sim, temos o robô manipulador KUKA de 6 eixos, código M09403124, na área de Parts Handling."
        },
        {
            "query": "Equipamentos de inspeção na funilaria",
            "context": "Área: FUNILARIA | UTE: Quality Control | Código: M09404567 | Descrição: Sistema de visão 3D para inspeção dimensional",
            "response": "Na área de Quality Control temos o sistema de visão 3D M09404567 para inspeção dimensional."
        },

        # ===== PINTURA (5 casos) =====
        {
            "query": "Qual o código do robô de pintura?",
            "context": "Área: PINTURA | UTE: Paint Shop Line 1 | Código: M08700012 | Descrição: Robô de pintura automatizado ABB 7 eixos",
            "response": "O código do robô de pintura é M08700012, um robô ABB de 7 eixos localizado na Paint Shop Line 1."
        },
        {
            "query": "Sistema de cura de pintura",
            "context": "Área: PINTURA | UTE: Curing Oven | Código: M08701234 | Descrição: Forno de cura por infravermelho 180°C",
            "response": "O sistema de cura é o forno M08701234 que opera com infravermelho a 180°C, localizado na Curing Oven."
        },
        {
            "query": "Cabine de pintura principal",
            "context": "Área: PINTURA | UTE: Paint Booth 1 | Código: M08702456 | Descrição: Cabine de pintura com sistema de exaustão e filtração",
            "response": "A cabine principal é a M08702456 na Paint Booth 1, equipada com sistema de exaustão e filtração."
        },
        {
            "query": "Equipamento de preparação de tinta",
            "context": "Área: PINTURA | UTE: Paint Kitchen | Código: M08703789 | Descrição: Sistema de dosagem e mistura automática de tinta",
            "response": "O equipamento de preparação é o sistema M08703789 na Paint Kitchen, com dosagem e mistura automática."
        },
        {
            "query": "Sistema de limpeza antes da pintura",
            "context": "Área: PINTURA | UTE: Pre-treatment | Código: M08704012 | Descrição: Túnel de lavagem e fosfatização 12 estágios",
            "response": "O sistema de limpeza é o túnel M08704012 no Pre-treatment com 12 estágios de lavagem e fosfatização."
        },

        # ===== MONTAGEM (5 casos) =====
        {
            "query": "Estação de montagem do motor",
            "context": "Área: MONTAGEM | UTE: Engine Assembly | Código: M11200345 | Descrição: Estação robotizada para montagem de motor",
            "response": "A estação de montagem do motor é a M11200345 no Engine Assembly, totalmente robotizada."
        },
        {
            "query": "Sistema de parafusadeiras da montagem",
            "context": "Área: MONTAGEM | UTE: Final Assembly Line | Código: M11201678 | Descrição: Parafusadeira elétrica com controle de torque",
            "response": "O sistema de parafusadeiras é o M11201678 na Final Assembly Line, com controle eletrônico de torque."
        },
        {
            "query": "Equipamento de teste de portas",
            "context": "Área: MONTAGEM | UTE: Door Assembly | Código: M11202901 | Descrição: Bancada de teste de abertura e fechamento de portas",
            "response": "A bancada de teste de portas é a M11202901 no Door Assembly, para teste de abertura e fechamento."
        },
        {
            "query": "Sistema de elevação de chassis",
            "context": "Área: MONTAGEM | UTE: Chassis Line | Código: M11203234 | Descrição: Sistema de elevação hidráulico para chassis",
            "response": "O sistema de elevação é o M11203234 na Chassis Line, com acionamento hidráulico."
        },
        {
            "query": "Estação de instalação de vidros",
            "context": "Área: MONTAGEM | UTE: Glass Installation | Código: M11204567 | Descrição: Estação robotizada para instalação de para-brisas",
            "response": "A estação é a M11204567 no Glass Installation, robotizada para instalação de para-brisas."
        },

        # ===== UTILIDADES (5 casos) =====
        {
            "query": "Mostre equipamentos de resfriamento",
            "context": "Área: GENERAL SERVICES | UTE: Chiller Plant | Código: M10500045 | Descrição: Chiller de água gelada 500 TR",
            "response": "Encontrei o chiller M10500045 na Chiller Plant, com capacidade de 500 TR para água gelada."
        },
        {
            "query": "Sistema de ar comprimido",
            "context": "Área: GENERAL SERVICES | UTE: Compressor Room | Código: M10501234 | Descrição: Compressor de ar parafuso 200 HP",
            "response": "O sistema de ar comprimido usa o compressor M10501234 de parafuso com 200 HP na Compressor Room."
        },
        {
            "query": "Equipamento de tratamento de água",
            "context": "Área: GENERAL SERVICES | UTE: Water Treatment | Código: M10502567 | Descrição: Sistema de osmose reversa 10.000 L/h",
            "response": "O tratamento de água usa o sistema M10502567 de osmose reversa com vazão de 10.000 L/h."
        },
        {
            "query": "Gerador de emergência",
            "context": "Área: GENERAL SERVICES | UTE: Power House | Código: M10503890 | Descrição: Gerador diesel 1500 kVA trifásico",
            "response": "O gerador de emergência é o M10503890 na Power House, diesel com 1500 kVA trifásico."
        },
        {
            "query": "Sistema de exaustão da planta",
            "context": "Área: GENERAL SERVICES | UTE: Ventilation System | Código: M10504123 | Descrição: Ventilador centrífugo 50.000 m³/h",
            "response": "O sistema de exaustão utiliza o ventilador centrífugo M10504123 com capacidade de 50.000 m³/h."
        }
    ]

    print(f"📋 Executando {len(test_cases)} avaliações...")
    print("⏱️  Isso pode levar alguns minutos...\n")

    # Executar avaliações
    results = judge.evaluate_batch(test_cases)

    # Exportar resultados
    output_file = "test_judge_extended_results.json"
    judge.export_evaluation_report(results, output_file)

    print(f"\n✅ Bateria de testes concluída!")
    print(f"📄 Resultados detalhados salvos em: {output_file}")
    print(f"\n{'='*60}")
    print("📊 ANÁLISE POR ÁREA:")
    print(f"{'='*60}")

    # Análise por área
    areas = {
        "FUNILARIA": results[:5],
        "PINTURA": results[5:10],
        "MONTAGEM": results[10:15],
        "UTILIDADES": results[15:20]
    }

    for area_name, area_results in areas.items():
        scores = [r['evaluation']['overall_score'] for r in area_results]
        avg_score = sum(scores) / len(scores)
        print(f"\n🏭 {area_name}:")
        print(f"   Score médio: {avg_score:.2f}/5.0")
        print(f"   Range: {min(scores):.1f} - {max(scores):.1f}")

    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    run_extended_tests()
