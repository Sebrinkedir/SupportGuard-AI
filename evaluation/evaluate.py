import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from main import run_supportguard
from single_agent import run_single_agent

# Test queries covering all 4 topics
# Test queries covering all 4 topics
TEST_QUERIES = [
    "I was charged twice this month and I want a refund.",
    "I cannot log into my account.",
    "Can I share my account with someone else?",
]

STABILITY_QUERY = "I was charged twice this month and I want a refund."


def evaluate_single_agent():
    """Run single agent on all test queries and measure hallucination and compliance."""
    print("\n[SINGLE AGENT] Running baseline...")
    print("-"*60)

    total = 0
    hallucination_count = 0
    compliant_count = 0

    for query in TEST_QUERIES:
        result = run_single_agent(query)
        response = result["response"].lower()
        total += 1

        # Check for hallucination — did it promise a refund directly?
        if "i will refund" in response or "you will receive a refund" in response or "refund has been processed" in response:
            hallucination_count += 1

        # Check policy compliance — did it avoid promising refunds directly?
        if "contact" in response or "support team" in response or "cannot process" in response or "unable to process" in response:
            compliant_count += 1

        print(f"Query: {query[:50]}...")
        print(f"Response preview: {result['response'][:100]}...")
        print()

    hr = round(hallucination_count / total, 4)
    pcs = round(compliant_count / total, 4)

    print(f"Single Agent Hallucination Rate : {hr}")
    print(f"Single Agent Policy Compliance  : {pcs}")
    print(f"Single Agent Stability          : Not measured (no RAS)")

    return {"hallucination_rate": hr, "policy_compliance": pcs}


def run_evaluation():
    print("\n" + "="*60)
    print("   SUPPORTGUARD-AI EVALUATION REPORT")
    print("="*60)

    # EXPERIMENT 1: Multi-Agent Results
    print("\n[EXPERIMENT 1] Multi-Agent System — Test Queries")
    print("-"*60)

    total_queries = 0
    total_hallucination = 0
    total_compliant = 0
    all_ras = []

    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        result = run_supportguard(query)

        hr = result["reliability"]["hallucination_rate"]
        pcs = result["reliability"]["policy_compliance_score"]
        ras = result["arbitration"]["average_ras"]
        reliability = result["reliability"]["reliability_score"]

        total_queries += 1
        total_hallucination += hr
        total_compliant += pcs
        all_ras.append(ras)

        print(f"  Hallucination Rate : {hr}")
        print(f"  Policy Compliant   : {pcs}")
        print(f"  Average RAS        : {ras}")
        print(f"  Reliability Score  : {reliability}")

    avg_hr = round(total_hallucination / total_queries, 4)
    avg_pcs = round(total_compliant / total_queries, 4)
    avg_ras = round(sum(all_ras) / len(all_ras), 4)

    print("\n" + "-"*60)
    print("MULTI-AGENT SUMMARY:")
    print(f"  Avg Hallucination Rate : {avg_hr}")
    print(f"  Avg Policy Compliance  : {avg_pcs}")
    print(f"  Avg RAS                : {avg_ras}")

    # EXPERIMENT 2: Stability Testing
    print("\n[EXPERIMENT 2] Stability Testing — 5 Runs Same Query")
    print("-"*60)
    print(f"Query: {STABILITY_QUERY}")

    stability_ras = []
    for i in range(3):
        print(f"\n  Run {i+1}:")
        result = run_supportguard(STABILITY_QUERY)
        ras = result["arbitration"]["average_ras"]
        stability_ras.append(ras)
        print(f"    RAS: {ras}")

    mean = sum(stability_ras) / len(stability_ras)
    variance = sum((x - mean) ** 2 for x in stability_ras) / len(stability_ras)
    std_dev = round(variance ** 0.5, 4)
    stability = round(1 - std_dev, 4)

    print(f"\n  RAS across runs : {stability_ras}")
    print(f"  Std Deviation   : {std_dev}")
    print(f"  Stability Score : {stability}")

    # EXPERIMENT 3: Real Single Agent vs Multi Agent
    print("\n[EXPERIMENT 3] Single Agent vs Multi-Agent Comparison")
    print("-"*60)
    single_results = evaluate_single_agent()

    print("\n" + "-"*60)
    print("FINAL COMPARISON:")
    print(f"{'Metric':<30} {'Single Agent':>15} {'Multi-Agent':>15}")
    print("-"*60)
    print(f"{'Hallucination Rate':<30} {single_results['hallucination_rate']:>15} {avg_hr:>15}")
    print(f"{'Policy Compliance':<30} {single_results['policy_compliance']:>15} {avg_pcs:>15}")
    print(f"{'Stability':<30} {'Not measured':>15} {stability:>15}")

    # Save Report
    report = {
        "multi_agent_summary": {
            "avg_hallucination_rate": avg_hr,
            "avg_policy_compliance": avg_pcs,
            "avg_ras": avg_ras
        },
        "stability": {
            "ras_scores": stability_ras,
            "std_deviation": std_dev,
            "stability_score": stability
        },
        "single_agent_results": {
            "hallucination_rate": single_results["hallucination_rate"],
            "policy_compliance": single_results["policy_compliance"]
        },
        "comparison": {
            "hallucination_improvement": round(single_results["hallucination_rate"] - avg_hr, 4),
            "compliance_improvement": round(avg_pcs - single_results["policy_compliance"], 4)
        }
    }

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/evaluation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "="*60)
    print("  Evaluation complete! Report saved to outputs/evaluation_report.json")
    print("="*60)


if __name__ == "__main__":
    run_evaluation()