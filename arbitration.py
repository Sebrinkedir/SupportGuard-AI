import logging
from config import AGENT_WEIGHTS, SEVERITY_SCORES, RAS_THRESHOLD

logger = logging.getLogger(__name__)

def calculate_ras(agent_outputs: list) -> dict:
    """
    Response Agreement Score (RAS) Arbitration.
    RAS(i) = (sum of wa * Si * Ca,i) / (sum of wa)
    """

    approved_fragments = []
    rejected_fragments = []
    ras_scores = []

    total_weight = sum(AGENT_WEIGHTS.values())

    for output in agent_outputs:
        agent_name = output.get("agent")
        confidence = output.get("confidence_score", 0)
        severity_label = output.get("severity", "low")
        fragment = output.get("response_fragment", "")

        weight = AGENT_WEIGHTS.get(agent_name, 0.1)
        severity = SEVERITY_SCORES.get(severity_label, 0.2)

        # Correct RAS formula: (wa * Si * Ca,i) / total_weight
        ras = (weight * severity * confidence) / total_weight
        ras = round(ras, 4)
        ras_scores.append(ras)

        logger.info(f"Agent: {agent_name} | Weight: {weight} | Severity: {severity} | Confidence: {confidence} | RAS: {ras}")

        if ras >= RAS_THRESHOLD:
            approved_fragments.append({
                "agent": agent_name,
                "fragment": fragment,
                "ras": ras
            })
        else:
            rejected_fragments.append({
                "agent": agent_name,
                "fragment": fragment,
                "ras": ras
            })

    return {
        "approved_fragments": approved_fragments,
        "rejected_fragments": rejected_fragments,
        "ras_scores": ras_scores,
        "average_ras": round(sum(ras_scores) / len(ras_scores), 4) if ras_scores else 0
    }


def build_final_response(arbitration_result: dict) -> str:
    """
    Builds the final customer response from approved fragments.
    """
    approved = arbitration_result["approved_fragments"]

    if not approved:
        return "We're sorry, we could not generate a verified response at this time. Please contact our support team directly."

    priority = {"policy": 1, "factual": 2, "intent": 3, "tone": 4}
    approved.sort(key=lambda x: priority.get(x["agent"], 5))

    # Use only top 2 highest RAS fragments for cleaner response
    approved_sorted = sorted(approved, key=lambda x: x["ras"], reverse=True)
    combined = " ".join([f["fragment"] for f in approved_sorted[:2]])
    return combined