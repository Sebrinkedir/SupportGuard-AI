import json
import os # to find file path 

def query_faq(topic: str) -> dict:
    """
    MCP Tool: Search the FAQ document by topic.
    Returns all FAQs matching the given topic.
    """
    
    # Build the path to the faq.json file
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'faq.json')
    
    # Open and read the file
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    # Search for matching topic
    results = [faq for faq in data['faqs'] if faq['topic'] == topic]
    
    # Return results
    if results:
        return {"status": "found", "topic": topic, "results": results}
    else:
        return {"status": "not_found", "topic": topic, "results": []}