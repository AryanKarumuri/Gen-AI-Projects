import streamlit as st
from langchain_groq import ChatGroq

# Initialize API key and LLM
api_key = "your_api_key"  # Ensure you put your actual API key here
if api_key:
    llm = ChatGroq(groq_api_key=api_key, model_name="Gemma2-9b-It")

def model_response(messages):
    # Ensure the messages are formatted correctly for llm.invoke()
    response = llm.invoke(messages)
    return response

st.markdown(
    "<style>header { position: fixed; top: 0; width: 100%; } </style>",
    unsafe_allow_html=True,
)

st.header("Chat with Sam👩‍💻")

if "messages" not in st.session_state:
    st.session_state.messages = []

user_avatar = "👩‍💻"
assistant_avatar = "🤖"

# Display existing messages
for message in st.session_state["messages"]:
    with st.chat_message(
        message["role"],
        avatar=assistant_avatar if message["role"] == "assistant" else user_avatar,
    ):
        st.markdown(message["content"])

# Input from user
if prompt := st.chat_input("How can I help you?"):
    if not api_key:
        st.info("Please add your API Key")
        st.stop()

    # Append user's message to session state
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=user_avatar):  
        st.markdown(prompt)

    # Pass entire session state messages
    response = model_response(st.session_state["messages"])  
    
    # Debug: Print the response to understand its structure
    #st.write("Raw response from the model:")
    #st.json(response)  

    try:
        msg = response.content        
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
    except AttributeError:
        st.error(f"Expected content attribute, but got: {response}")
