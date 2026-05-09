from config import AGENT_WEIGHTS, SEVERITY_SCORES, RAS_THRESHOLD

def calculate_ras(agent_outputs: list) -> dict:
    """
    Response Agreement Score (RAS) Arbitration.
    Calculates RAS for each agent output and filters fragments.
    """

    approved_fragments = []
    rejected_fragments = []
    ras_scores = []

    for output in agent_outputs:
        agent_name = output.get("agent")
        confidence = output.get("confidence_score", 0)
        severity_label = output.get("severity", "low")
        fragment = output.get("response_fragment", "")

        # Get weight and severity score from config
        weight = AGENT_WEIGHTS.get(agent_name, 0.1)
        severity = SEVERITY_SCORES.get(severity_label, 0.2)

        # Calculate RAS for this fragment
        # RAS = (weight * severity * confidence) / weight
        ras = (weight * severity * confidence) / weight
        ras = round(ras, 4)
        ras_scores.append(ras)

        # Apply threshold filter
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

    # Sort by agent priority - policy first, then factual, intent, tone
    priority = {"policy": 1, "factual": 2, "intent": 3, "tone": 4}
    approved.sort(key=lambda x: priority.get(x["agent"], 5))

    # Combine fragments into final response
    combined = " ".join([f["fragment"] for f in approved])
    return combined