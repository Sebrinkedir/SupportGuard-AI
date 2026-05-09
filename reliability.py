def calculate_reliability(hallucination_rate: float, 
                           policy_compliance_score: float, 
                           ras_scores: list,
                           alpha: float = 0.4, 
                           beta: float = 0.4, 
                           gamma: float = 0.2) -> dict:
    """
    Formal Reliability Model.
    R = α(1 - HR) + βPCS + γStability
    
    HR  = Hallucination Rate (unsupported claims / total claims)
    PCS = Policy Compliance Score (fraction of compliant responses)
    Stability = 1 - standard deviation of RAS scores across runs
    """

    # Calculate stability from RAS scores
    if len(ras_scores) > 1:
        mean = sum(ras_scores) / len(ras_scores)
        variance = sum((x - mean) ** 2 for x in ras_scores) / len(ras_scores)
        std_dev = variance ** 0.5
        stability = round(1 - std_dev, 4)
    else:
        stability = 1.0

    # Calculate R
    R = alpha * (1 - hallucination_rate) + beta * policy_compliance_score + gamma * stability
    R = round(R, 4)

    return {
        "reliability_score": R,
        "hallucination_rate": hallucination_rate,
        "policy_compliance_score": policy_compliance_score,
        "stability": stability,
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma,
        "formula": "R = α(1 - HR) + βPCS + γStability"
    }