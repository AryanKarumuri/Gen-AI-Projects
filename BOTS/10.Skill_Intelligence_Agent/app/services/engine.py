import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()

from langchain_community.utilities import SearxSearchWrapper
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

SEARX_HOST = os.getenv("SEARX_HOST")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
NUM_RESULTS_DEFAULT = int(os.getenv("NUM_RESULTS_DEFAULT", "10"))


SYSTEM_PROMPT = PromptTemplate(
    input_variables=["query", "search_results"],
    template="""You are a Skill Intelligence Engine. Your job is to find libraries and tools alternatives for any given topic. Analyze the query and search results, then return a structured JSON object.

Query: {query}

Web Search Results:
{search_results}

Instructions:
1. Write a 2-3 sentence summary of \"{query}\" based on the search results.
2. Extract ONLY concrete, named, installable libraries or tools — things a developer can pip install or directly use with \"{query}\".
   - Do not limit to 3. Extract as many as are genuinely relevant.
   - Include both foundational skills and advanced ones.
3. Return ONLY valid JSON. No markdown fences, no explanation, no extra text.

Output format:
{{
  "{query}": "<2-3 sentence summary>",
  "Relevant Skills": {{
    "<Skill Name>": "<1 sentence description of what it is and why it matters for this topic>",
    "<Skill Name>": "<1 sentence description>",
    ...
  }},
  "Sources": ["<url1>", "<url2>", ...],
  "Skill Names Only": ["Skill1", "Skill2", "Skill3", ...]
}}
"""
)


def _strip_json_fences(raw: str) -> str:
    clean = raw.strip()
    for fence in ["```json", "```"]:
        if clean.startswith(fence):
            clean = clean[len(fence) :]
    if clean.endswith("```"):
        clean = clean[:-3]
    return clean.strip()


def run_engine(query: str, num_results: int = NUM_RESULTS_DEFAULT) -> Dict[str, Any]:
    sources: List[str] = []
    search_text = ""

    try:
        search = SearxSearchWrapper(searx_host=SEARX_HOST)
        results = search.results(
            f"{query} libraries tools technologies alternatives", num_results=num_results
        )

        if not results:
            raise ValueError("No results returned")

        chunks: List[str] = []
        for r in results:
            url = r.get("link", "")
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            if url:
                sources.append(url)
            chunks.append(f"Title: {title}\nSnippet: {snippet}\nURL: {url}")

        search_text = "\n\n".join(chunks)
        print(f"[SearXNG] Fetched {len(results)} results", file=sys.stderr)

    except Exception as e:
        print(f"[WARN] SearXNG unavailable ({e}) — falling back to model knowledge", file=sys.stderr)
        search_text = (
            f"No live search results available. "
            f"Use your training knowledge to list ALL skills relevant to: {query}"
        )

    print(f"[Ollama] Generating with model '{OLLAMA_MODEL}'...", file=sys.stderr)
    llm = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
    prompt_text = SYSTEM_PROMPT.format(query=query, search_results=search_text)
    raw = llm.invoke(prompt_text)

    cleaned = _strip_json_fences(raw)
    try:
        result = json.loads(cleaned)
        if sources and "Sources" not in result:
            result["Sources"] = sources
        return result
    except json.JSONDecodeError:
        return {
            "raw_response": raw,
            "parse_error": "LLM did not return valid JSON. Try a larger model.",
            "sources": sources,
        }
