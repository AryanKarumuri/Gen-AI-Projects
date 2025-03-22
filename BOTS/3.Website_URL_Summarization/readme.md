# Website URL Summarizer

This project is a **Website URL Summarizer** that extracts and summarizes content from a given URL using **LangChain** and **Google Gemini API**. It provides a simple and interactive user interface using **Streamlit**.

## Features

- Extracts content from a specified URL using **UnstructuredURLLoader**.
- Cleans and preprocesses the text using functions like `remove_punctuation` and `clean_extra_whitespace`.
- Summarizes the extracted content using **Google Gemini API** and **LangChain's map-reduce summarization chain**.
- Displays the generated summary using **Streamlit**.

## Prerequisites

You can install the dependencies using the following command:

```bash
pip install -r requirements.txt
```

## How It Works

### Content Extraction:
- The URL content is fetched using **UnstructuredURLLoader**.
- Punctuation and unnecessary whitespace are removed using the **remove_punctuation** and **clean_extra_whitespace** functions.

### Summarization:
- The cleaned content is passed to a **Gemini 1.5 Pro** LLM using **LangChain's** `load_summarize_chain` with the **map_reduce** method.
- The summary is generated and returned.

### Streamlit UI:
- Users input a URL through a simple web interface.