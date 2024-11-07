# Gemini Q&A Bot using Streamlit and Google Generative AI

This is a simple web-based Q&A bot built using Streamlit and Google Generative AI(Gemini). The bot allows users to ask questions, and it retrieves answers using the Gemini language model.

## Features

- **Interactive UI**: Built with Streamlit to provide a user-friendly interface.
- **Generative Responses**: Uses Google's Gemini API to generate responses to user queries.
- **Easy to Deploy**: Simple to run locally or deploy to platforms like Streamlit sharing or other cloud services.

## Requirements

To run this project locally, you need:

- Python 3.10
- Streamlit
- Google Generative AI API client

## Setup Instructions

### Step-1: Install the required dependencies
Make sure to install the dependencies using the below command.

```bash
  pip -m install requirements.txt
```

### Step-2: Getting Gemini API key
- Go to [Google AI Studio](https://aistudio.google.com)
- Sign-in with the Google account.
- Click on API Key.
- Click on Create API Key.
- Make sure to save the generated API Key.

### Step-3: Set up the API key
- Once you have the API key, you need to add it to your Streamlit secrets file. Create a `.streamlit/secrets.toml` file in your project directory with the following content:
  ```bash
    [API_KEY]
    gemini_api_key = "your_api_key_here"
  ```
**Note:** Here in this repository, you won't find the `secrets.toml` since I made the code deployed on Streamlit. If you want to deploy the code on Streamlit, check [Gen-AI-Projects README.md](../../README.md)


### Step-4: Running the App
- After installing the dependencies and setting up your API key, you can run the app using Streamlit:
  ```bash
    streamlit run main.py
  ```
**Note:** Please ensure that you don't share sensitive API keys in public repositories. Always use secret management techniques for production applications.


















