from crewai.tools import tool
from ddgs import DDGS
from typing import Union, List, Dict, Any

@tool
def web_search_tool(query: Union[str, Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Searches the web and returns results.
    Accepts a string query, If a dictionary is passed, it will try to extract a string safely.
    """
    # Handle list of queries
    if isinstance(query, list):
        results = []
        for q in query:
            if isinstance(q, dict):
                # Extract the actual query string from nested structure
                q_str = _extract_query_string(q)
            else:
                q_str = str(q)
            results.append(_perform_search(q_str))
        return {"results": results, "query_count": len(query)}
    
    # Handle single dictionary query
    if isinstance(query, dict):
        query_str = _extract_query_string(query)
    else:
        # Handle string query
        query_str = str(query)
    
    # Perform the search
    search_result = _perform_search(query_str)
    return {"results": search_result, "query": query_str}

def _extract_query_string(query_dict: Dict[str, Any]) -> str:
    """
    Extracts the actual query string from various possible dictionary structures.
    """
    # Handle nested structure like {"query": {"task": "..."}} 
    if "query" in query_dict:
        inner_query = query_dict["query"]
        if isinstance(inner_query, dict) and "task" in inner_query:
            return inner_query["task"]
        elif isinstance(inner_query, str):
            return inner_query
    
    # Handle direct task structure like {"task": "..."}
    if "task" in query_dict:
        return query_dict["task"]
    
    # Handle other common keys
    return (query_dict.get("description") or 
            query_dict.get("search") or 
            query_dict.get("text") or 
            str(query_dict))

def _perform_search(query: str) -> Dict[str, Any]:
    """
    Performs the actual web search using DDGS.
    """
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
        return {"results": str(results), "query": query, "status": "success"}
    except Exception as e:
        return {"error": str(e), "query": query, "status": "error"}