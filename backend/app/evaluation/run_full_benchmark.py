"""
run_full_benchmark.py

Script completo de benchmark para métricas do paper ICEIS 2026
Executa todas as avaliações: Dataset Stats, RAG Metrics, System Performance, LLM Judge
"""

import sys
import os
from dotenv import load_dotenv
import json
import time
from datetime import datetime

# Carregar .env
load_dotenv()

# Adicionar o diretório app ao path
sys.path.insert(0, os.path.abspath('.'))

from app.evaluation.llm_judge import LLMJudge
from app.evaluation.evaluation_service import EvaluationService


def print_section_header(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def run_dataset_statistics():
    """1. Estatísticas do Dataset"""
    print_section_header("📊 PARTE 1: ESTATÍSTICAS DO DATASET")

    eval_service = EvaluationService()
    stats = eval_service.get_dataset_statistics()

    print(f"✅ Total de Equipamentos: {stats['total_equipments']}")
    print(f"\n📍 Distribuição por Área:")
    for area, count in sorted(stats['by_area'].items(), key=lambda x: x[1], reverse=True):
        pct = (count / stats['total_equipments'] * 100) if stats['total_equipments'] > 0 else 0
        print(f"   {area:30s}: {count:4d} ({pct:5.2f}%)")

    print(f"\n🏗️  Cobertura Hierárquica:")
    h = stats['hierarchy_coverage']
    print(f"   Com UTE:       {h['with_ute']:4d} ({h['with_ute']/stats['total_equipments']*100:5.2f}%)")
    print(f"   Com Linha:     {h['with_linha']:4d} ({h['with_linha']/stats['total_equipments']*100:5.2f}%)")
    print(f"   Com Estação:   {h['with_estacao']:4d} ({h['with_estacao']/stats['total_equipments']*100:5.2f}%)")
    print(f"   Com Código:    {h['with_codigo']:4d} ({h['with_codigo']/stats['total_equipments']*100:5.2f}%)")
    print(f"   Hierarquia Completa: {h['complete_hierarchy']:4d} ({h['completeness_rate']:.2f}%)")

    return stats


def run_rag_evaluation():
    """2. Avaliação RAG (Retrieval)"""
    print_section_header("🔍 PARTE 2: RAG RETRIEVAL METRICS")

    eval_service = EvaluationService()

    print("Executando avaliação de retrieval...")
    print("⏱️  Isso pode levar alguns minutos...\n")

    rag_results = eval_service.evaluate_rag_retrieval(top_k=5)

    print(f"✅ Queries Testadas: {rag_results['total_queries_tested']}")
    print(f"\n📊 Métricas de Retrieval:")
    print(f"   Success Rate:       {rag_results['success_rate']:.2f}%")
    print(f"   Avg Retrieval Time: {rag_results['avg_retrieval_time_ms']:.2f}ms")
    print(f"   Avg Results/Query:  {rag_results['avg_results_per_query']:.2f}")

    return rag_results


def run_system_performance():
    """3. Performance do Sistema"""
    print_section_header("⚡ PARTE 3: SYSTEM PERFORMANCE METRICS")

    eval_service = EvaluationService()

    print("Executando benchmark de performance...")
    print("⏱️  Testando velocidade de busca vetorial e geração de embeddings...\n")

    perf_results = eval_service.benchmark_system_performance(iterations=20)

    print(f"✅ Iterações: {perf_results['iterations']}")
    print(f"\n🔍 Vector Search Performance:")
    print(f"   Avg Time:  {perf_results['vector_search']['avg_ms']:.2f}ms")
    print(f"   Min Time:  {perf_results['vector_search']['min_ms']:.2f}ms")
    print(f"   Max Time:  {perf_results['vector_search']['max_ms']:.2f}ms")

    print(f"\n📝 Embedding Generation:")
    print(f"   Avg Time:  {perf_results['embedding_generation']['avg_ms']:.2f}ms")
    print(f"   Min Time:  {perf_results['embedding_generation']['min_ms']:.2f}ms")
    print(f"   Max Time:  {perf_results['embedding_generation']['max_ms']:.2f}ms")

    return perf_results


def run_llm_judge_evaluation():
    """4. LLM-as-a-Judge Evaluation"""
    print_section_header("🤖 PARTE 4: LLM-AS-A-JUDGE EVALUATION")

    judge = LLMJudge()

    # Casos de teste para LLM Judge
    test_cases = [
        # FUNILARIA
        {
            "query": "Quais são os robôs de solda na funilaria?",
            "context": "Área: FUNILARIA | UTE: Body Shop Line 1 | Código: M09400123 | Descrição: Robô de solda 6 eixos",
            "response": "Na funilaria temos o robô de solda M09400123 de 6 eixos na Body Shop Line 1."
        },
        {
            "query": "Equipamentos de prensa",
            "context": "Área: FUNILARIA | UTE: Press Shop | Código: M09401567 | Descrição: Prensa hidráulica 500 ton",
            "response": "Encontrei a prensa hidráulica M09401567 de 500 toneladas no Press Shop."
        },
        # PINTURA
        {
            "query": "Robô de pintura principal",
            "context": "Área: PINTURA | UTE: Paint Shop Line 1 | Código: M08700012 | Descrição: Robô de pintura ABB",
            "response": "O robô de pintura principal é o M08700012 da ABB na Paint Shop Line 1."
        },
        {
            "query": "Sistema de cura",
            "context": "Área: PINTURA | UTE: Curing Oven | Código: M08701234 | Descrição: Forno IR 180°C",
            "response": "O sistema de cura usa o forno M08701234 com infravermelho a 180°C."
        },
        # MONTAGEM
        {
            "query": "Estação de montagem do motor",
            "context": "Área: MONTAGEM | UTE: Engine Assembly | Código: M11200345 | Descrição: Estação robotizada",
            "response": "A estação de montagem do motor é a M11200345 no Engine Assembly."
        },
        {
            "query": "Sistema de parafusadeiras",
            "context": "Área: MONTAGEM | UTE: Final Assembly | Código: M11201678 | Descrição: Parafusadeira torque",
            "response": "O sistema de parafusadeiras é o M11201678 com controle de torque."
        },
        # UTILIDADES
        {
            "query": "Equipamento de resfriamento",
            "context": "Área: GENERAL SERVICES | UTE: Chiller Plant | Código: M10500045 | Descrição: Chiller 500 TR",
            "response": "O chiller M10500045 tem capacidade de 500 TR."
        },
        {
            "query": "Compressor de ar",
            "context": "Área: GENERAL SERVICES | UTE: Compressor Room | Código: M10501234 | Descrição: Compressor 200 HP",
            "response": "O compressor M10501234 tem 200 HP de potência."
        },
    ]

    print(f"Avaliando {len(test_cases)} respostas com LLM Judge...")
    print("⏱️  Isso pode levar alguns minutos...\n")

    results = judge.evaluate_batch(test_cases)

    # Calcular médias
    scores = {
        'relevance': [],
        'technical_accuracy': [],
        'completeness': [],
        'grounding': [],
        'clarity': [],
        'faithfulness': [],
        'overall_score': []
    }

    for result in results:
        eval_data = result['evaluation']
        for key in scores.keys():
            scores[key].append(eval_data[key])

    avg_scores = {key: sum(values) / len(values) for key, values in scores.items()}

    print(f"✅ Total Avaliações: {len(results)}")
    print(f"\n📊 Scores Médios:")
    print(f"   Overall Score:        {avg_scores['overall_score']:.2f}/5.0")
    print(f"   Relevance:            {avg_scores['relevance']:.2f}/5.0")
    print(f"   Technical Accuracy:   {avg_scores['technical_accuracy']:.2f}/5.0")
    print(f"   Completeness:         {avg_scores['completeness']:.2f}/5.0")
    print(f"   Grounding:            {avg_scores['grounding']:.2f}/5.0")
    print(f"   Clarity:              {avg_scores['clarity']:.2f}/5.0")
    print(f"   Faithfulness:         {avg_scores['faithfulness']:.2f}/5.0")

    return {
        'total_evaluations': len(results),
        'average_scores': avg_scores,
        'detailed_results': results
    }


def run_full_benchmark():
    """Executa o benchmark completo"""
    print("\n" + "=" * 70)
    print("  🚀 BENCHMARK COMPLETO - ICEIS 2026 PAPER")
    print("=" * 70)
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    start_time = time.time()

    # Coletar todas as métricas
    benchmark_results = {
        'timestamp': datetime.now().isoformat(),
        'dataset_statistics': None,
        'rag_metrics': None,
        'system_performance': None,
        'llm_judge': None
    }

    try:
        # 1. Dataset Statistics
        benchmark_results['dataset_statistics'] = run_dataset_statistics()

        # 2. RAG Evaluation
        benchmark_results['rag_metrics'] = run_rag_evaluation()

        # 3. System Performance
        benchmark_results['system_performance'] = run_system_performance()

        # 4. LLM Judge
        benchmark_results['llm_judge'] = run_llm_judge_evaluation()

    except Exception as e:
        print(f"\n❌ Erro durante benchmark: {e}")
        import traceback
        traceback.print_exc()

    # Tempo total
    total_time = time.time() - start_time
    benchmark_results['total_execution_time'] = round(total_time, 2)

    # Salvar resultados
    output_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(benchmark_results, f, indent=2, ensure_ascii=False)

    # Resumo final
    print_section_header("✅ BENCHMARK CONCLUÍDO")
    print(f"⏱️  Tempo Total: {total_time:.2f}s ({total_time/60:.2f} minutos)")
    print(f"📄 Resultados salvos em: {output_file}")

    # Resumo executivo
    print(f"\n📊 RESUMO EXECUTIVO:")
    if benchmark_results['dataset_statistics']:
        print(f"   Equipamentos no Dataset: {benchmark_results['dataset_statistics']['total_equipments']}")

    if benchmark_results['rag_metrics']:
        print(f"   RAG Success Rate: {benchmark_results['rag_metrics']['success_rate']:.2f}%")
        print(f"   RAG Avg Time: {benchmark_results['rag_metrics']['avg_retrieval_time_ms']:.2f}ms")

    if benchmark_results['system_performance']:
        print(f"   Avg Vector Search: {benchmark_results['system_performance']['vector_search']['avg_ms']:.2f}ms")
        print(f"   Avg Embedding Gen: {benchmark_results['system_performance']['embedding_generation']['avg_ms']:.2f}ms")

    if benchmark_results['llm_judge']:
        print(f"   LLM Judge Overall: {benchmark_results['llm_judge']['average_scores']['overall_score']:.2f}/5.0")

    print("\n" + "=" * 70 + "\n")

    return benchmark_results


if __name__ == "__main__":
    run_full_benchmark()
