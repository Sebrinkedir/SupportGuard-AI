import os
import json
import logging
from dotenv import load_dotenv
from google import genai

load_dotenv()
logger = logging.getLogger(__name__)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def run_single_agent(customer_query: str) -> dict:
    """
    Single Agent Baseline.
    Just one raw Gemini call - no tools, no RAS, no arbitration.
    Used for comparison against the multi-agent system.
    """

    prompt = f"""
    You are a customer support assistant.
    Answer the following customer query as best you can.

    Customer Query: {customer_query}

    Provide a helpful, polite response.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return {
            "query": customer_query,
            "response": response.text.strip(),
            "agent_type": "single"
        }
    except Exception as e:
        logger.error(f"Single agent error: {e}")
        return {
            "query": customer_query,
            "response": "Error generating response.",
            "agent_type": "single"
        }