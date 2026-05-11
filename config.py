# Agent weights for RAS calculation
AGENT_WEIGHTS = {
    "intent": 0.30,
    "policy": 0.35,
    "factual": 0.25,
    "tone": 0.10
}

# Severity scores
SEVERITY_SCORES = {
    "high": 1.0,
    "medium": 0.6,
    "low": 0.2
}

# RAS threshold - fragments below this are rejected
RAS_THRESHOLD = 0.08

# Gemini model to use
MODEL_NAME = "gemini-2.5-flash"