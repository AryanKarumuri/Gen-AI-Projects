# Chat with Sam using LangChain and Groq API

This Streamlit app integrates the LangChain framework and the Groq API to create an interactive chat experience. The app allows users to converse with an AI model (Gemma2-9b-It) via a simple web interface.

## Features

- **Interactive Chat**: Users can input queries, and the assistant responds in real time.
- **Customizable**: You can replace the API key with your own for accessing the Groq API and use your favourite model.
- **Chat History**: The app displays the full conversation history on the interface, so users can see the entire chat history as they interact with the assistant.

## Requirements

To run this application locally, you need to install the following dependencies:

- Python 3.7+
- Streamlit
- langchain
- `langchain_groq` library (for integrating Groq with LangChain)

## Setup

1. **Get Your Groq API Key:** You need a valid API key from Groq to interact with the model. Replace "your_api_key" in the code with your actual API key.
   Check here for creating a new one Readme.md

2. **Install dependencies:**: Run the following command to install all the dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit App:** Run the app using the following command

   ```bash
   streamlit run main.py
   ```

## Debugging

The raw response from the model can be debugged by uncommenting the following line:

  ```bash
  # st.write("Raw response from the model:")
  # st.json(response)
  ```
This will display the raw content returned by the model, which can help you troubleshoot any issues with the response format.

## Troubleshooting
- **Missing API Key:** Ensure that you have entered a valid API key in the api_key variable.
- **Invalid Response Format:** If the assistant does not respond as expected, check the structure of the response to ensure it contains a content attribute.
