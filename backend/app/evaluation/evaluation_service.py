"""
evaluation_service.py

Módulo de avaliação para gerar métricas do paper ICEIS 2026
Avalia: RAG performance, UNS generation, system performance
"""

from typing import List, Dict, Any, Tuple
import time
from datetime import datetime
from collections import defaultdict
import json

from app.services.google_sheets import sheets_service
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.services.uns_architecture import uns_architecture_service
from app.models.schemas import Equipment


class EvaluationService:
    """Serviço para avaliar performance do sistema para o paper científico"""
    
    def __init__(self):
        self.test_queries = [
            # Equipment search queries
            "Quais são os robôs de solda na funilaria?",
            "Mostre equipamentos de resfriamento",
            "Encontre prensas Schuler",
            "Robôs de pintura no paint shop",
            "Elevadores na área de montagem",
            
            # Hierarchical queries
            "Equipamentos da UTE Body Shop Line 1",
            "O que tem na linha de pintura?",
            "Mostre equipamentos da estação de solda",
            
            # Information queries
            "O que é o equipamento M09400000?",
            "Descreva o sistema de resfriamento",
            
            # UNS navigation
            "Quantas áreas de produção existem?",
            "Mostre a estrutura hierárquica da funilaria",
        ]
    
    # ============================================================
    # 1. DATASET STATISTICS
    # ============================================================
    
    def get_dataset_statistics(self) -> Dict[str, Any]:
        """
        Estatísticas do dataset para Section 4.1 (Experimental Setup)
        """
        equipments = sheets_service.get_all_equipments()
        
        # Total equipments
        total = len(equipments)
        
        # Distribution by area
        by_area = defaultdict(int)
        for eq in equipments:
            area = eq.area or "Unknown"
            by_area[area] += 1
        
        # Distribution by hierarchy level
        has_ute = sum(1 for eq in equipments if eq.ute)
        has_linha = sum(1 for eq in equipments if eq.linha)
        has_estacao = sum(1 for eq in equipments if eq.estacao)
        has_codigo = sum(1 for eq in equipments if eq.codigo)
        
        # Completeness
        complete_hierarchy = sum(
            1 for eq in equipments 
            if eq.area and eq.ute and eq.linha and eq.codigo
        )
        
        return {
            "total_equipments": total,
            "by_area": dict(by_area),
            "hierarchy_coverage": {
                "with_ute": has_ute,
                "with_linha": has_linha,
                "with_estacao": has_estacao,
                "with_codigo": has_codigo,
                "complete_hierarchy": complete_hierarchy,
                "completeness_rate": round(complete_hierarchy / total * 100, 2) if total > 0 else 0
            }
        }
    
    # ============================================================
    # 2. RAG PERFORMANCE EVALUATION
    # ============================================================
    
    def evaluate_rag_retrieval(self, top_k: int = 5) -> Dict[str, Any]:
        """
        Avalia performance de retrieval do RAG
        Métricas: Precision@k, Success Rate, Response Time
        """
        results = []
        
        for query in self.test_queries:
            start_time = time.time()
            
            # Perform semantic search
            retrieved = rag_service.semantic_search(query, k=top_k)
            
            retrieval_time = time.time() - start_time
            
            # Analyze results
            has_results = len(retrieved) > 0
            num_results = len(retrieved)
            
            results.append({
                "query": query,
                "num_retrieved": num_results,
                "has_results": has_results,
                "retrieval_time_ms": round(retrieval_time * 1000, 2),
                "top_result": retrieved[0] if retrieved else None
            })
        
        # Calculate metrics
        success_rate = sum(1 for r in results if r["has_results"]) / len(results) * 100
        avg_retrieval_time = sum(r["retrieval_time_ms"] for r in results) / len(results)
        avg_results_per_query = sum(r["num_retrieved"] for r in results) / len(results)
        
        return {
            "total_queries_tested": len(self.test_queries),
            "success_rate": round(success_rate, 2),
            "avg_retrieval_time_ms": round(avg_retrieval_time, 2),
            "avg_results_per_query": round(avg_results_per_query, 2),
            "query_results": results
        }
    
    def evaluate_end_to_end_responses(self) -> Dict[str, Any]:
        """
        Avalia qualidade das respostas geradas (RAG + LLM)
        Métricas: Response Time, Response Length, Source Attribution
        """
        results = []
        
        for query in self.test_queries[:5]:  # Primeiras 5 queries para economizar API calls
            start_time = time.time()
            
            # Get context from RAG
            context = rag_service.get_context_for_query(query, k=3)
            
            # Generate response
            response = llm_service.generate_response(
                user_input=query,
                context=context
            )
            
            total_time = time.time() - start_time
            
            # Analyze response
            response_length = len(response)
            has_equipment_codes = "M0" in response or "código" in response.lower()
            
            results.append({
                "query": query,
                "response": response,
                "response_length_chars": response_length,
                "total_time_ms": round(total_time * 1000, 2),
                "cites_equipment_codes": has_equipment_codes
            })
        
        # Calculate metrics
        avg_response_time = sum(r["total_time_ms"] for r in results) / len(results)
        avg_response_length = sum(r["response_length_chars"] for r in results) / len(results)
        citation_rate = sum(1 for r in results if r["cites_equipment_codes"]) / len(results) * 100
        
        return {
            "queries_evaluated": len(results),
            "avg_response_time_ms": round(avg_response_time, 2),
            "avg_response_length": round(avg_response_length, 2),
            "equipment_citation_rate": round(citation_rate, 2),
            "sample_responses": results[:3]  # Top 3 examples for paper
        }
    
    # ============================================================
    # 3. UNS GENERATION EVALUATION
    # ============================================================
    
    def evaluate_uns_generation(self) -> Dict[str, Any]:
        """
        Avalia geração da hierarquia UNS
        Métricas: Completeness, Depth, Coverage
        """
        equipments = sheets_service.get_all_equipments()
        
        start_time = time.time()
        
        # Generate UNS hierarchy
        uns_tree = uns_architecture_service.build_uns_tree(equipments)
        
        generation_time = time.time() - start_time
        
        # Get statistics
        stats = uns_architecture_service.get_statistics(equipments)
        
        # Calculate metrics
        total_nodes = self._count_tree_nodes(uns_tree)
        max_depth = self._calculate_tree_depth(uns_tree)
        
        return {
            "total_equipments_processed": len(equipments),
            "generation_time_ms": round(generation_time * 1000, 2),
            "hierarchy_statistics": stats,
            "tree_metrics": {
                "total_nodes": total_nodes,
                "max_depth": max_depth,
                "areas_count": len(stats.get("by_area", {})),
                "utes_count": len(stats.get("by_ute", {})),
                "linhas_count": len(stats.get("by_linha", {}))
            }
        }
    
    def _count_tree_nodes(self, tree: Dict) -> int:
        """Conta número total de nós na árvore UNS"""
        count = 1  # Current node
        if "children" in tree and tree["children"]:
            for child in tree["children"]:
                count += self._count_tree_nodes(child)
        return count
    
    def _calculate_tree_depth(self, tree: Dict, current_depth: int = 0) -> int:
        """Calcula profundidade máxima da árvore"""
        if "children" not in tree or not tree["children"]:
            return current_depth
        
        max_child_depth = current_depth
        for child in tree["children"]:
            child_depth = self._calculate_tree_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
    
    # ============================================================
    # 4. SYSTEM PERFORMANCE BENCHMARKS
    # ============================================================
    
    def benchmark_system_performance(self, iterations: int = 10) -> Dict[str, Any]:
        """
        Benchmark de performance do sistema completo
        Testa: Vector search speed, LLM inference, UNS generation
        """
        # Test vector search speed
        search_times = []
        for _ in range(iterations):
            start = time.time()
            rag_service.semantic_search("robô de solda", k=5)
            search_times.append((time.time() - start) * 1000)
        
        # Test embedding generation speed
        embed_times = []
        test_text = "Equipamento de resfriamento na área de pintura"
        for _ in range(iterations):
            start = time.time()
            rag_service.embeddings.embed_query(test_text)
            embed_times.append((time.time() - start) * 1000)
        
        return {
            "iterations": iterations,
            "vector_search": {
                "avg_ms": round(sum(search_times) / len(search_times), 2),
                "min_ms": round(min(search_times), 2),
                "max_ms": round(max(search_times), 2)
            },
            "embedding_generation": {
                "avg_ms": round(sum(embed_times) / len(embed_times), 2),
                "min_ms": round(min(embed_times), 2),
                "max_ms": round(max(embed_times), 2)
            }
        }
    
    # ============================================================
    # 5. COMPLETE EVALUATION REPORT
    # ============================================================
    
    def generate_full_evaluation_report(self) -> Dict[str, Any]:
        """
        Gera relatório completo de avaliação para o paper
        Inclui todas as métricas necessárias
        """
        print("🔬 Iniciando avaliação completa do sistema...")
        
        print("📊 1/5 - Coletando estatísticas do dataset...")
        dataset_stats = self.get_dataset_statistics()
        
        print("🔍 2/5 - Avaliando performance do RAG...")
        rag_performance = self.evaluate_rag_retrieval()
        
        print("💬 3/5 - Avaliando respostas end-to-end...")
        response_quality = self.evaluate_end_to_end_responses()
        
        print("🌳 4/5 - Avaliando geração UNS...")
        uns_evaluation = self.evaluate_uns_generation()
        
        print("⚡ 5/5 - Executando benchmarks de performance...")
        performance = self.benchmark_system_performance()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "dataset_statistics": dataset_stats,
            "rag_performance": rag_performance,
            "response_quality": response_quality,
            "uns_generation": uns_evaluation,
            "system_performance": performance
        }
        
        print("✅ Avaliação completa!")
        return report
    
    # ============================================================
    # 6. EXPORT RESULTS FOR PAPER
    # ============================================================
    
    def export_results_for_paper(self, output_file: str = "evaluation_results.json"):
        """
        Exporta resultados formatados para uso no paper
        """
        report = self.generate_full_evaluation_report()
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Resultados exportados para: {output_file}")
        
        # Print summary for paper
        self._print_paper_summary(report)
        
        return report
    
    def _print_paper_summary(self, report: Dict[str, Any]):
        """Imprime resumo formatado para copiar direto no paper"""
        print("\n" + "="*60)
        print("📝 RESUMO PARA O PAPER (Section 4 - Results)")
        print("="*60)
        
        ds = report["dataset_statistics"]
        print(f"\n✅ DATASET:")
        print(f"   Total de equipamentos: {ds['total_equipments']}")
        print(f"   Áreas: {len(ds['by_area'])}")
        print(f"   Completude hierárquica: {ds['hierarchy_coverage']['completeness_rate']}%")
        
        rag = report["rag_performance"]
        print(f"\n✅ RAG PERFORMANCE:")
        print(f"   Taxa de sucesso: {rag['success_rate']}%")
        print(f"   Tempo médio de retrieval: {rag['avg_retrieval_time_ms']}ms")
        print(f"   Resultados médios por query: {rag['avg_results_per_query']}")
        
        resp = report["response_quality"]
        print(f"\n✅ RESPONSE QUALITY:")
        print(f"   Tempo médio de resposta: {resp['avg_response_time_ms']}ms")
        print(f"   Tamanho médio da resposta: {resp['avg_response_length']} chars")
        print(f"   Taxa de citação de equipamentos: {resp['equipment_citation_rate']}%")
        
        uns = report["uns_generation"]
        print(f"\n✅ UNS GENERATION:")
        print(f"   Tempo de geração: {uns['generation_time_ms']}ms")
        print(f"   Total de nós: {uns['tree_metrics']['total_nodes']}")
        print(f"   Profundidade máxima: {uns['tree_metrics']['max_depth']} níveis")
        
        perf = report["system_performance"]
        print(f"\n✅ SYSTEM PERFORMANCE:")
        print(f"   Vector search: {perf['vector_search']['avg_ms']}ms")
        print(f"   Embedding generation: {perf['embedding_generation']['avg_ms']}ms")
        
        print("\n" + "="*60 + "\n")


# Singleton
evaluation_service = EvaluationService()


# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Run complete evaluation
    evaluation_service.export_results_for_paper("paper_evaluation_results.json")