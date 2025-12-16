import streamlit as st
import sys
import os
import json

# Add the parent directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

st.set_page_config(
    page_title="Diabetes Risk Prediction",
    page_icon="💊",
    layout="centered",
)

from agent_src.crew import create_prediction_crew

st.sidebar.title("⚙️ Settings")

if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = ""

st.session_state.groq_api_key = st.sidebar.text_input(
    "🔑 Groq API key",
    type="password",
    value=st.session_state.groq_api_key,
    help="Paste your Groq API key here. Sidebar can be collapsed.",
)

st.sidebar.caption("You can collapse this panel from the top-left arrow.")

st.title("🩺📊 Diabetes Risk Prediction")
st.write("Enter patient data to predict diabetes risk.")

with st.form("patient_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pregnancies = st.number_input("Pregnancies", min_value=0, max_value=20, value=0)
        glucose = st.number_input("Glucose", min_value=0, max_value=300, value=100)
        blood_pressure = st.number_input("Blood Pressure", min_value=0, max_value=200, value=80)
    with col2:
        skin_thickness = st.number_input("Skin Thickness", min_value=0, max_value=99, value=35)
        insulin = st.number_input("Insulin", min_value=0, max_value=900, value=85)
        bmi = st.number_input("BMI", min_value=0.0, max_value=70.0, value=25.0)
    with col3:
        diabetes_pedigree = st.number_input("Diabetes Pedigree Function", min_value=0.0, max_value=2.5, value=0.2)
        age = st.number_input("Age", min_value=0, max_value=120, value=25)
    submitted = st.form_submit_button("Predict")

if submitted:
    if not st.session_state.groq_api_key:
        st.error("Please enter your Groq API key in the sidebar.")
        st.stop()
    
    prediction_crew = create_prediction_crew(st.session_state.groq_api_key)
    
    patient_data = {
        "Pregnancies": pregnancies,
        "Glucose": glucose,
        "BloodPressure": blood_pressure,
        "SkinThickness": skin_thickness,
        "Insulin": insulin,
        "BMI": bmi,
        "DiabetesPedigreeFunction": diabetes_pedigree,
        "Age": age
    }
    
    result = prediction_crew.kickoff(inputs={"patient_data": patient_data})
    
    try:
        clean_json = result.raw.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json.replace("```json", "").replace("```", "")
        
        diabetes_pred = json.loads(clean_json)

    except Exception as e:
        st.error(f"Error parsing result: {e}")
        st.write("Raw Output:", result.raw)
        st.stop()

    tool_output = diabetes_pred.get("tool_output", {})
    

    if isinstance(tool_output, str):
         try:
             tool_output = json.loads(tool_output)
         except:
             tool_output = {}

    colA, colB = st.columns(2)
    with colA:
        st.subheader("Result")
        st.metric(label="🍩🩸Diabetes Risk", value=tool_output.get('result', 'N/A'))

    with colB:
        st.subheader("Probability Diabetic")        
        st.metric(label="Probability", value=tool_output.get('probability', 'N/A'))

    st.subheader("Summary")    
    st.success(diabetes_pred.get('prediction_summary', 'N/A'))

    st.subheader("📚Explanation")
    if diabetes_pred.get("explanation", []):
        st.table({"Explanation": diabetes_pred.get("explanation", [])})
    else:
        st.write("No explanation available.")

    st.subheader("💡Actionable Health Advice")
    if diabetes_pred.get("recommendations", []):
        st.table({"Advice": diabetes_pred.get("recommendations", [])})
    else:
        st.write("No advice available.")

    st.caption("⚠️ Disclaimer:  This is a screening estimate, not a diagnosis. Please consult a certified healthcare professional for a comprehensive evaluation and personalized advice.")

    with st.expander("Raw Tool Output"):
        st.json(tool_output)
