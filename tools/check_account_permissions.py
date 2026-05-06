import json
import os

def check_account_permissions(action: str) -> dict:
    """
    MCP Tool: Check if a specific account action is permitted.
    Returns permission rules for the given action.
    """
    
    # Build the path to the account_permissions.json file
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'account_permissions.json')
    
    # Open and read the file
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    # Search for matching action
    results = [perm for perm in data['account_permissions'] if perm['action'] == action]
    
    # Return results
    if results:
        return {"status": "found", "action": action, "results": results}
    else:
        return {"status": "not_found", "action": action, "results": []}