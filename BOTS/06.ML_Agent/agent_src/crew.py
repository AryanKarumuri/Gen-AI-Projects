from crewai import Crew
from agent_src.agents import create_diabetes_agent
from agent_src.tasks import create_predict_diabetes_task

def create_prediction_crew(groq_api_key):
    # Create agent with the provided API key
    diabetes_agent = create_diabetes_agent(groq_api_key)
    
    # Create task with the agent
    predict_diabetes_task = create_predict_diabetes_task(diabetes_agent)
    
    prediction_crew = Crew(
        name="Diabetes Risk Assessment Crew",
        agents=[diabetes_agent],
        tasks=[predict_diabetes_task],
        verbose=True
    )
    
    return prediction_crew