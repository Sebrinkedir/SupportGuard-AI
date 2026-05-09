import os
import json
from dotenv import load_dotenv
from agents.intent_agent import run_intent_agent
from agents.policy_agent import run_policy_agent
from agents.factual_agent import run_factual_agent
from agents.tone_agent import run_tone_agent
from arbitration import calculate_ras, build_final_response
from reliability import calculate_reliability

load_dotenv()

def run_supportguard(customer_query: str) -> dict:
    """
    Main pipeline — runs all 4 agents, arbitration, and reliability scoring.
    """

    print("\n" + "="*60)
    print(f"Customer Query: {customer_query}")
    print("="*60)

    # Step 1 - Run all 4 agents
    print("\n[1] Running agents...")
    intent_output  = run_intent_agent(customer_query)
    policy_output  = run_policy_agent(customer_query)
    factual_output = run_factual_agent(customer_query)
    tone_output    = run_tone_agent(customer_query)

    agent_outputs = [intent_output, policy_output, factual_output, tone_output]
    print("    All agents completed.")

    # Step 2 - Run RAS arbitration
    print("\n[2] Running RAS arbitration...")
    arbitration_result = calculate_ras(agent_outputs)
    print(f"    Average RAS: {arbitration_result['average_ras']}")
    print(f"    Approved fragments: {len(arbitration_result['approved_fragments'])}")
    print(f"    Rejected fragments: {len(arbitration_result['rejected_fragments'])}")

    # Step 3 - Build final response
    print("\n[3] Building final response...")
    final_response = build_final_response(arbitration_result)
    print(f"    Final Response: {final_response}")

    # Step 4 - Calculate reliability
    print("\n[4] Calculating reliability...")
    unsupported = factual_output.get("unsupported_claims", [])
    supported   = factual_output.get("supported_claims", [])
    total_claims = len(unsupported) + len(supported)
    hallucination_rate = len(unsupported) / total_claims if total_claims > 0 else 0

    policy_compliant = 1.0 if policy_output.get("policy_compliant", False) else 0.0
    ras_scores = arbitration_result["ras_scores"]

    reliability = calculate_reliability(hallucination_rate, policy_compliant, ras_scores)
    print(f"    Reliability Score: {reliability['reliability_score']}")

    # Step 5 - Compile full result
    result = {
        "query": customer_query,
        "final_response": final_response,
        "arbitration": arbitration_result,
        "reliability": reliability,
        "agent_outputs": agent_outputs
    }

    # Step 6 - Save output to file
    os.makedirs("outputs", exist_ok=True)
    filename = f"outputs/response_{abs(hash(customer_query))}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n[5] Output saved to {filename}")

    return result


if __name__ == "__main__":
    # Test query
    test_query = "I was charged twice this month and I want a refund."
    run_supportguard(test_query)