"""
test_judge.py

Script simples para testar o LLM Judge
Rode: python test_judge.py
"""

import sys
import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

# Adicionar o diretório app ao path
sys.path.insert(0, os.path.abspath('.'))

# Importar o LLM Judge
from app.evaluation.llm_judge import LLMJudge

def test_simple():
    """Teste simples com 1 query"""
    print("🚀 Testando LLM Judge...\n")
    
    # Inicializar (vai pegar GROQ_API_KEY do ambiente)
    judge = LLMJudge()
    
    # Caso de teste simples
    result = judge.evaluate_response(
        query="Quais são os robôs de solda na funilaria?",
        context="Área: FUNILARIA | UTE: Body Shop Line 1 | Código: M09400123 | Descrição: Robô de solda 6 eixos para painéis laterais",
        response="Na área de funilaria, especificamente na Body Shop Line 1, temos o robô de solda código M09400123. Este é um robô de 6 eixos utilizado para soldagem de painéis laterais."
    )
    
    print("\n✅ RESULTADO DA AVALIAÇÃO:")
    print(f"   Overall Score: {result['overall_score']}/5.0")
    print(f"   Relevance: {result['relevance']}/5.0")
    print(f"   Technical Accuracy: {result['technical_accuracy']}/5.0")
    print(f"   Grounding: {result['grounding']}/5.0")
    print(f"   Faithfulness: {result['faithfulness']}/5.0")
    print(f"\n   Justification: {result['justification']}")
    print(f"   Strengths: {result['strengths']}")
    
    print("\n🎉 Teste concluído com sucesso!")

def test_batch():
    """Teste com múltiplas queries"""
    print("🚀 Testando LLM Judge com batch...\n")
    
    judge = LLMJudge()
    
    test_cases = [
        {
            "query": "Quais são os robôs de solda na funilaria?",
            "context": "Área: FUNILARIA | Código: M09400123 | Descrição: Robô de solda 6 eixos",
            "response": "Na funilaria temos o robô M09400123 de 6 eixos."
        },
        {
            "query": "Mostre equipamentos de resfriamento",
            "context": "Área: GENERAL SERVICES | Código: M10500045 | Descrição: Chiller de água gelada",
            "response": "Encontrei o chiller M10500045 para água gelada."
        },
        {
            "query": "Qual o código do robô de pintura?",
            "context": "Área: PINTURA | Código: M08700012 | Descrição: Robô de pintura automatizado",
            "response": "O código é M08700012."
        }
    ]
    
    results = judge.evaluate_batch(test_cases)
    judge.export_evaluation_report(results, "test_judge_results.json")
    
    print("\n🎉 Teste batch concluído!")
    print("📄 Resultados salvos em: test_judge_results.json")

if __name__ == "__main__":
    # Escolha qual teste rodar:
    
    print("Escolha o teste:")
    print("1 - Teste simples (1 query)")
    print("2 - Teste batch (3 queries)")
    
    choice = input("\nDigite 1 ou 2: ").strip()
    
    if choice == "1":
        test_simple()
    elif choice == "2":
        test_batch()
    else:
        print("❌ Opção inválida!")