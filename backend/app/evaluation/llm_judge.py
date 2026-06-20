"""
llm_judge.py

LLM-as-a-Judge evaluation module using Groq API
Avalia qualidade das respostas do sistema para o paper científico ICEIS 2026

INSTALAÇÃO:
    pip install groq

USO:
    from llm_judge import LLMJudge
    
    judge = LLMJudge(api_key="sua_chave_groq")
    
    result = judge.evaluate_response(
        query="Quais são os robôs de solda?",
        context="Área: FUNILARIA | Código: M09400123 | Descrição: Robô de solda 6 eixos",
        response="Na funilaria temos o robô M09400123 de 6 eixos."
    )
    
    print(result)
"""

from typing import Dict, List, Any, Tuple
import os
from groq import Groq
import json
import time
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()


class LLMJudge:
    """
    LLM-as-a-Judge para avaliar qualidade das respostas
    Usa Groq API (LLaMA 3.1 70B) como juiz imparcial
    """
    
    def __init__(self, api_key: str = None):
        """
        Inicializa o LLM Judge
        
        Args:
            api_key: Chave da API Groq (se None, pega de GROQ_API_KEY env var)
        """
        self.client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
        self.judge_model = "llama-3.3-70b-versatile"  # Modelo maior = melhor julgamento
    
    # ============================================================
    # PROMPT DE AVALIAÇÃO
    # ============================================================
    
    EVALUATION_PROMPT = """Você é um avaliador especializado em sistemas de IA para indústria.
Avalie a resposta gerada pelo sistema considerando os seguintes critérios:

**QUERY DO USUÁRIO:**
{query}

**CONTEXTO RECUPERADO (RAG):**
{context}

**RESPOSTA GERADA:**
{response}

---

**AVALIE OS SEGUINTES CRITÉRIOS (escala 1-5):**

1. **RELEVÂNCIA** (1-5): A resposta está relacionada à pergunta?
   - 1: Completamente irrelevante
   - 3: Parcialmente relevante
   - 5: Perfeitamente relevante

2. **PRECISÃO TÉCNICA** (1-5): A resposta está tecnicamente correta?
   - 1: Informação incorreta
   - 3: Parcialmente correta
   - 5: Totalmente precisa

3. **COMPLETUDE** (1-5): A resposta é completa e satisfatória?
   - 1: Muito incompleta
   - 3: Parcialmente completa
   - 5: Totalmente completa

4. **FUNDAMENTAÇÃO** (1-5): A resposta cita as fontes corretamente?
   - 1: Não cita fontes
   - 3: Cita algumas fontes
   - 5: Bem fundamentada com códigos de equipamentos

5. **CLAREZA** (1-5): A resposta é clara e bem escrita?
   - 1: Confusa
   - 3: Razoavelmente clara
   - 5: Muito clara

6. **FIDELIDADE AO CONTEXTO** (1-5): A resposta usa apenas informação do contexto?
   - 1: Alucina bastante
   - 3: Algumas extrapolações
   - 5: Fiel ao contexto

**RETORNE APENAS UM JSON** no seguinte formato:
```json
{{
  "relevance": <1-5>,
  "technical_accuracy": <1-5>,
  "completeness": <1-5>,
  "grounding": <1-5>,
  "clarity": <1-5>,
  "faithfulness": <1-5>,
  "overall_score": <média>,
  "justification": "<breve justificativa em 1-2 frases>",
  "strengths": "<pontos fortes>",
  "weaknesses": "<pontos fracos>"
}}
```

NÃO inclua nenhum texto adicional, APENAS o JSON."""

    # ============================================================
    # AVALIAÇÃO DE UMA ÚNICA RESPOSTA
    # ============================================================
    
    def evaluate_response(
        self, 
        query: str, 
        context: str, 
        response: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Avalia uma única resposta usando LLM-as-a-Judge
        
        Args:
            query: Pergunta do usuário
            context: Contexto recuperado pelo RAG
            response: Resposta gerada pelo sistema
            max_retries: Número de tentativas em caso de erro
            
        Returns:
            Dict com scores e justificativas
        """
        prompt = self.EVALUATION_PROMPT.format(
            query=query,
            context=context[:1000],  # Limita contexto para não estourar tokens
            response=response
        )
        
        for attempt in range(max_retries):
            try:
                completion = self.client.chat.completions.create(
                    model=self.judge_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é um avaliador técnico especializado. Retorne APENAS JSON válido."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.1,  # Baixa temperatura para avaliação consistente
                    max_tokens=500
                )
                
                judgment_text = completion.choices[0].message.content.strip()
                
                # Extrair JSON (remover markdown se houver)
                if "```json" in judgment_text:
                    judgment_text = judgment_text.split("```json")[1].split("```")[0].strip()
                elif "```" in judgment_text:
                    judgment_text = judgment_text.split("```")[1].split("```")[0].strip()
                
                # Parse JSON
                judgment = json.loads(judgment_text)
                
                # Validar campos obrigatórios
                required_fields = ["relevance", "technical_accuracy", "completeness", 
                                 "grounding", "clarity", "faithfulness", "overall_score"]
                
                if all(field in judgment for field in required_fields):
                    return judgment
                else:
                    print(f"⚠️ Tentativa {attempt + 1}: JSON incompleto")
                    
            except json.JSONDecodeError as e:
                print(f"⚠️ Tentativa {attempt + 1}: Erro ao parsear JSON - {e}")
                if attempt == max_retries - 1:
                    return self._neutral_evaluation(f"Parse error: {e}")
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Erro na avaliação: {e}")
                if attempt == max_retries - 1:
                    return self._neutral_evaluation(f"Error: {e}")
                time.sleep(1)
        
        return self._neutral_evaluation("Max retries exceeded")
    
    def _neutral_evaluation(self, error_msg: str) -> Dict[str, Any]:
        """Retorna avaliação neutra em caso de erro"""
        return {
            "relevance": 3,
            "technical_accuracy": 3,
            "completeness": 3,
            "grounding": 3,
            "clarity": 3,
            "faithfulness": 3,
            "overall_score": 3.0,
            "justification": f"Avaliação automática falhou: {error_msg}",
            "strengths": "N/A",
            "weaknesses": "N/A",
            "error": True
        }
    
    # ============================================================
    # AVALIAÇÃO EM BATCH
    # ============================================================
    
    def evaluate_batch(
        self, 
        test_cases: List[Dict[str, str]],
        delay_between_calls: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Avalia múltiplas respostas
        
        Args:
            test_cases: Lista de dicts com 'query', 'context', 'response'
            delay_between_calls: Delay em segundos entre chamadas (rate limiting)
            
        Returns:
            Lista de avaliações
        """
        results = []
        
        print(f"🔬 Avaliando {len(test_cases)} respostas com LLM-as-a-Judge...")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"   [{i}/{len(test_cases)}] Avaliando query: {test_case['query'][:50]}...")
            
            evaluation = self.evaluate_response(
                query=test_case['query'],
                context=test_case['context'],
                response=test_case['response']
            )
            
            results.append({
                "query": test_case['query'],
                "response": test_case['response'],
                "evaluation": evaluation
            })
            
            # Rate limiting
            if i < len(test_cases):
                time.sleep(delay_between_calls)
        
        print(f"✅ Avaliação concluída!")
        return results
    
    # ============================================================
    # MÉTRICAS AGREGADAS
    # ============================================================
    
    def calculate_aggregate_metrics(
        self, 
        evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calcula métricas agregadas das avaliações
        
        Returns:
            Dict com médias, distribuições e estatísticas
        """
        if not evaluations:
            return {}
        
        # Extrair scores
        all_scores = {
            "relevance": [],
            "technical_accuracy": [],
            "completeness": [],
            "grounding": [],
            "clarity": [],
            "faithfulness": [],
            "overall_score": []
        }
        
        for eval_result in evaluations:
            evaluation = eval_result.get("evaluation", {})
            for metric in all_scores.keys():
                if metric in evaluation:
                    all_scores[metric].append(evaluation[metric])
        
        # Calcular médias
        averages = {
            metric: round(sum(scores) / len(scores), 2) if scores else 0
            for metric, scores in all_scores.items()
        }
        
        # Distribuição de scores
        score_distribution = {
            "excellent (4.5-5.0)": 0,
            "good (3.5-4.4)": 0,
            "fair (2.5-3.4)": 0,
            "poor (1.5-2.4)": 0,
            "very_poor (1.0-1.4)": 0
        }
        
        for score in all_scores["overall_score"]:
            if score >= 4.5:
                score_distribution["excellent (4.5-5.0)"] += 1
            elif score >= 3.5:
                score_distribution["good (3.5-4.4)"] += 1
            elif score >= 2.5:
                score_distribution["fair (2.5-3.4)"] += 1
            elif score >= 1.5:
                score_distribution["poor (1.5-2.4)"] += 1
            else:
                score_distribution["very_poor (1.0-1.4)"] += 1
        
        # Calcular percentuais
        total = len(all_scores["overall_score"])
        score_distribution_pct = {
            category: round(count / total * 100, 1) if total > 0 else 0
            for category, count in score_distribution.items()
        }
        
        return {
            "num_evaluations": len(evaluations),
            "average_scores": averages,
            "score_distribution": score_distribution,
            "score_distribution_percentage": score_distribution_pct,
            "criteria_ranking": self._rank_criteria(averages)
        }
    
    def _rank_criteria(self, averages: Dict[str, float]) -> List[Tuple[str, float]]:
        """Rankeia critérios por performance"""
        criteria = {k: v for k, v in averages.items() if k != "overall_score"}
        return sorted(criteria.items(), key=lambda x: x[1], reverse=True)
    
    # ============================================================
    # EXPORT PARA O PAPER
    # ============================================================
    
    def export_evaluation_report(
        self, 
        evaluations: List[Dict[str, Any]],
        output_file: str = "llm_judge_evaluation.json"
    ) -> Dict[str, Any]:
        """
        Exporta relatório completo de avaliação
        """
        aggregate = self.calculate_aggregate_metrics(evaluations)
        
        report = {
            "metadata": {
                "judge_model": self.judge_model,
                "num_test_cases": len(evaluations),
                "evaluation_date": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "aggregate_metrics": aggregate,
            "detailed_evaluations": evaluations
        }
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        self._print_summary(aggregate)
        
        print(f"\n📄 Relatório completo salvo em: {output_file}")
        
        return report
    
    def _print_summary(self, aggregate: Dict[str, Any]):
        """Imprime resumo formatado"""
        print("\n" + "="*60)
        print("📊 LLM-AS-A-JUDGE EVALUATION RESULTS")
        print("="*60)
        
        avgs = aggregate["average_scores"]
        print(f"\n✅ AVERAGE SCORES:")
        print(f"   Overall Score:        {avgs['overall_score']}/5.0")
        print(f"   Relevance:            {avgs['relevance']}/5.0")
        print(f"   Technical Accuracy:   {avgs['technical_accuracy']}/5.0")
        print(f"   Completeness:         {avgs['completeness']}/5.0")
        print(f"   Grounding (Sources):  {avgs['grounding']}/5.0")
        print(f"   Clarity:              {avgs['clarity']}/5.0")
        print(f"   Faithfulness:         {avgs['faithfulness']}/5.0")
        
        dist_pct = aggregate["score_distribution_percentage"]
        print(f"\n📊 SCORE DISTRIBUTION:")
        print(f"   Excellent (4.5-5.0): {dist_pct['excellent (4.5-5.0)']}%")
        print(f"   Good (3.5-4.4):      {dist_pct['good (3.5-4.4)']}%")
        print(f"   Fair (2.5-3.4):      {dist_pct['fair (2.5-3.4)']}%")
        print(f"   Poor (1.5-2.4):      {dist_pct['poor (1.5-2.4)']}%")
        
        print(f"\n🏆 BEST PERFORMING CRITERIA:")
        for i, (criterion, score) in enumerate(aggregate["criteria_ranking"][:3], 1):
            print(f"   {i}. {criterion}: {score}/5.0")
        
        print("\n" + "="*60 + "\n")


# ============================================================
# EXEMPLO DE USO
# ============================================================

if __name__ == "__main__":
    print("🚀 Exemplo de uso do LLM Judge\n")
    
    # Initialize judge
    judge = LLMJudge()
    
    # Example test cases
    test_cases = [
        {
            "query": "Quais são os robôs de solda na funilaria?",
            "context": "Área: FUNILARIA | UTE: Body Shop Line 1 | Código: M09400123 | Descrição: Robô de solda 6 eixos para painéis laterais",
            "response": "Na área de funilaria, especificamente na Body Shop Line 1, temos o robô de solda código M09400123. Este é um robô de 6 eixos utilizado para soldagem de painéis laterais."
        },
        {
            "query": "Mostre equipamentos de resfriamento",
            "context": "Área: GENERAL SERVICES | UTE: Utilities | Código: M10500045 | Descrição: Chiller de água gelada 500TR",
            "response": "Encontrei equipamentos de resfriamento no sistema. Há o chiller M10500045 de 500TR para água gelada, localizado na área de General Services."
        },
        {
            "query": "Qual o código do robô de pintura?",
            "context": "Área: PINTURA | UTE: Paint Line 2 | Código: M08700012 | Descrição: Robô de pintura automatizado",
            "response": "O código do robô de pintura é M08700012."
        }
    ]
    
    print("📝 Avaliando 3 respostas de exemplo...\n")
    
    # Run evaluation
    results = judge.evaluate_batch(test_cases, delay_between_calls=1.0)
    
    # Export report
    report = judge.export_evaluation_report(results, "example_llm_judge_results.json")
    
    print("\n✅ Exemplo concluído!")
    print("📄 Veja o arquivo 'example_llm_judge_results.json' para detalhes")