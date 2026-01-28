from pydantic import BaseModel
from typing import List, Optional, Any
from crewai import Task, Agent
from functools import partial
from agent_src.tools import predict_diabetes

class DiabetesPredictionSummary(BaseModel):
    result: str
    probability: float
    test_results: str

class DiabetesOutput(BaseModel):
    prediction_summary: DiabetesPredictionSummary
    explanation: List[str]
    recommendations: List[str]
    tool_output: Any

# We'll create the task function that accepts an agent parameter
def create_predict_diabetes_task(agent: Agent):
    return Task(
        name="Diabetes Risk Prediction Task",
        agent=agent,
        description=(
            "This task involves assessing an individual's risk of developing diabetes based on their health data. "
            "patient_data: {patient_data}"
            "The agent will utilize the `predict_diabetes` tool to analyze the provided patient data and generate a comprehensive risk assessment. "
            "The output will include a summary of the prediction, an explanation of the factors influencing the risk, and actionable lifestyle recommendations."
        ),
        expected_output=(
            "A structured output containing:\n"
            "1. prediction_summary: A summary of the diabetes risk prediction including result, probability, and test results.\n"
            "2. explanation: A list of key factors that influenced the risk assessment.\n"
            "3. recommendations: A list of 3 specific lifestyle recommendations to mitigate diabetes risk.\n"
            "4. tool_output: The raw output from the `predict_diabetes` tool for reference."
        ),
        output_model=DiabetesOutput,
    )