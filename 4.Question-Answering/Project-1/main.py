import streamlit as st
import google.generativeai as genai

#API_KEY = ""#Generate your own API key 
gemini_api_key = st.secrets["API_KEY"]
genai.configure(api_key=gemini_api_key)
# Choose a Gemini model
model = genai.GenerativeModel("gemini-pro") 

# Function for getting a response from chosen model
def get_gemini_response(question):
    response = model.generate_content(question)
    return response.text

st.set_page_config(page_title="Question & Answring Bot")
st.header("Gemini Q&A Bot🤖")
query = st.text_input("Ask your question: ", key="input")
submit = st.button("Answer💡")

if submit:
    response = get_gemini_response(query)
    st.subheader("Here is the answer✨:")
    st.write(response)
