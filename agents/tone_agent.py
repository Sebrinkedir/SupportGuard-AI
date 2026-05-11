import os
import json
import logging
from dotenv import load_dotenv
from google import genai

load_dotenv()
logger = logging.getLogger(__name__)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def run_tone_agent(customer_query: str) -> dict:
    """
    Tone & Clarity Agent.
    FIX: Severity was hardcoded to "low" so tone agent was always rejected.
    Now the model assigns severity based on how emotional the query is.
    """

    prompt = f"""
    You are a Tone and Clarity Agent for a customer support system.

    Your job is to:
    1. Ensure the response is polite and empathetic
    2. Ensure the language is simple and easy to understand
    3. Ensure the response does not sound robotic or dismissive
    4. Provide a well worded customer friendly response fragment
    5. Assign a confidence score between 0 and 1
    6. Assign severity based on how important tone is for this query:
       - high: customer is upset, frustrated, or emotional
       - medium: neutral query that still benefits from warmth
       - low: simple factual request with no emotional context

    Customer Query: {customer_query}

    Respond in this exact JSON format:
    {{
        "tone_issues": ["issue1 or empty list if none"],
        "clarity_issues": ["issue1 or empty list if none"],
        "response_fragment": "A polite and clear response fragment",
        "severity": "high or medium or low",
        "confidence_score": 0.0
    }}

    Respond with JSON only. No extra text.
    """

    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        raw = response.text.strip().replace("```json", "").replace("```", "")
        result = json.loads(raw)
        result["agent"] = "tone"
        logger.info(f"Tone agent completed | severity: {result.get('severity')} | confidence: {result.get('confidence_score')}")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Tone agent JSON parse error: {e}")
        return {
            "agent": "tone",
            "tone_issues": [],
            "clarity_issues": [],
            "response_fragment": "We appreciate your patience and are happy to help you with this.",
            "severity": "medium",
            "confidence_score": 0.5,
            "error": "json_parse_error"
        }
    except Exception as e:
        logger.error(f"Tone agent unexpected error: {e}")
        return {
            "agent": "tone",
            "tone_issues": [],
            "clarity_issues": [],
            "response_fragment": "We appreciate your patience and are happy to help you with this.",
            "severity": "medium",
            "confidence_score": 0.5,
            "error": str(e)
        }