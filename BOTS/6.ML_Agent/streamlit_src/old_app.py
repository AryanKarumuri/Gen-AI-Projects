import streamlit as st
import sys
import os

# Add the parent directory to the Python path to make agent_src importable
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

st.title("⚕️Diabetes Risk Prediction")
st.write("Enter patient data to predict diabetes risk.")

with st.form("patient_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pregnancies = st.number_input("Pregnancies", min_value=0, max_value=20, value=1)
        glucose = st.number_input("Glucose", min_value=0, max_value=300, value=100)
        blood_pressure = st.number_input("Blood Pressure", min_value=0, max_value=200, value=70)
    with col2:
        skin_thickness = st.number_input("Skin Thickness", min_value=0, max_value=99, value=20)
        insulin = st.number_input("Insulin", min_value=0, max_value=900, value=85)
        bmi = st.number_input("BMI", min_value=0.0, max_value=70.0, value=22.5)
    with col3:
        diabetes_pedigree = st.number_input("Diabetes Pedigree Function", min_value=0.0, max_value=2.5, value=0.2)
        age = st.number_input("Age", min_value=0, max_value=120, value=25)
    submitted = st.form_submit_button("Predict")

if submitted:
    # Check if API key is provided
    if not st.session_state.groq_api_key:
        st.error("Please enter your Groq API key in the sidebar.")
        st.stop()
    
    # Create prediction crew with the provided API key
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
    diabetes_pred_dict = result.to_dict()
    diabetes_pred = diabetes_pred_dict.get("diabetes_risk_prediction", {})

    colA, colB = st.columns(2)
    with colA:
        st.subheader("Result")
        st.metric(label="Diabetes Risk", value=diabetes_pred.get('result', 'N/A'))
    with colB:
        st.subheader("Probability Diabetic")
        st.metric(label="Probability", value=diabetes_pred.get('probability_diabetic', 'N/A'))

    st.subheader("Summary")
    st.success(diabetes_pred.get('prediction_summary', 'N/A'))

    st.subheader("Explanation")
    if diabetes_pred_dict.get("explanation", []):
        st.table({"Explanation": diabetes_pred_dict.get("explanation", [])})
    else:
        st.write("No explanation available.")

    st.subheader("Actionable Health Advice")
    if diabetes_pred_dict.get("recommendations", []):
        st.table({"Advice": diabetes_pred_dict.get("recommendations", [])})
    else:
        st.write("No advice available.")

    with st.expander("Raw Tool Output"):
        st.json(diabetes_pred_dict.get("tool_output", {}))