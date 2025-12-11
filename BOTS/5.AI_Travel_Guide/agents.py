from crewai import Agent, LLM
from tools import web_search_tool
import logging

logging.basicConfig(level=logging.INFO)


def build_llm(api_key: str):
    """
    Create and return an LLM instance bound to the provided API key.
    """
    if not api_key:
        raise ValueError("API key required to build LLM")
    return LLM(
        model="mistral/ministral-8b-2512", 
        api_key=api_key,
        temperature=0.2,
    )


def build_agents(api_key: str):
    """
    Build and return (planner_agent, location_agent, guide_agent) configured
    with an LLM instance created from the provided api_key.
    """
    llm = build_llm(api_key)

    planner_agent = Agent(
        role="Chief Travel Logistician",
        goal="Synthesize research and suggestions into a logical, time-efficient, and budget-conscious itinerary.",
        backstory=(
            "You are a master logistician with 20 years of experience in the travel industry. "
            "Your strength lies in logistical feasibility—you know that a 10-minute gap isn't enough to catch a train. "
            "You take the raw data from the Researcher and the creative ideas from the Guide and weave them into a practical schedule."
        ),
        llm=llm,
        tools=[web_search_tool],
        verbose=True,
        allow_delegation=False,
    )

    location_agent = Agent(
        role="Destination Analyst",
        goal="Verify facts, assess safety, and provide critical logistical data (visas, weather, costs).",
        backstory=(
            "You are a meticulous data analyst who specializes in travel risk and preparation. "
            "You focus on facts: visa rules, weather, safety advisories, and local transport logistics."
        ),
        llm=llm,
        tools=[web_search_tool],
        verbose=True,
        allow_delegation=False,
    )

    guide_agent = Agent(
        role="Local Culture Insider",
        goal="Uncover hidden gems, authentic culinary experiences, and cultural nuances avoiding tourist traps.",
        backstory=(
            "You are a passionate local insider who hates standard tourist traps. "
            "You recommend things locals love, the best times to visit, and where to find authentic food and culture."
        ),
        llm=llm,
        tools=[web_search_tool],
        verbose=True,
        allow_delegation=False,
    )

    return planner_agent, location_agent, guide_agent
