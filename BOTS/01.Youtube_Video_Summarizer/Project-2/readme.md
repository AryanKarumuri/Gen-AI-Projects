# YouTube Video Summarizer with Google Gemini (Updated)

This is an updated version of **[Project-1](https://github.com/AryanKarumuri/Gen-AI-Projects/tree/main/BOTS/1.Youtube%20Video%20Summarizer/Project-1)**. The app now includes enhanced features, allowing for customizable summaries and keyword-based filtering of the transcript.

## Requirements

Before running the application, ensure you have the following Python libraries installed:

- `langchain==0.3.7`
- `streamlit==1.40.1`
- `google.generativeai==0.8.3`
- `langchain_community==0.3.6`

To install the required dependencies, you can use the provided `requirements.txt` file. Run the following command:

```bash
  pip install -r requirements.txt
```

## Add-On Features

The app has the following new features to enhance the summarization and search experience:

- **Select Summary Length**: Users can select the length of the summary (Short, Medium, or Long).
- **Search by Keyword**: Users can enter a keyword to filter and summarize specific sections of the transcript.

## Feature Details

### 1. Select Summary Length

After entering a YouTube URL, you can choose how detailed you'd like the summary to be. The available options are:

- **Short**: A concise summary with 4-5 key bullet points.
- **Medium**: A more detailed summary with 7-9 bullet points, capturing key details from the transcript.
- **Long**: A thorough summary with 10-13 bullet points, including comprehensive insights and details.

The app uses **Google Gemini's generative model** to generate the summary based on the selected length, ensuring the content is appropriately condensed or detailed according to your preference.

### 2. Search and Filter by Keyword

You can search for specific keywords or phrases within the transcript to filter out relevant sections. If a keyword is found, the app will generate a summary based only on the sections that contain that term.

- Enter a keyword or phrase in the search field to filter through the transcript.
- If matching sections are found, the app will summarize them based on the selected summary length.
- If no matching sections are found, the app will notify you that no relevant content was found for the provided search term.



