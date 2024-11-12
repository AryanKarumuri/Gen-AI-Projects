import os
import langchain
import streamlit as st
import google.generativeai as genai
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.youtube import TranscriptFormat

# Configuration and API key for Google Gemini
gemini_api_key = "your_api_key"
genai.configure(api_key=gemini_api_key)

def extract_video_transcript(youtube_link):
    """
    Extracts the video transcript from a YouTube video URL.
    This function loads the transcript in chunks and returns the full transcript text.
    """
    try:
        loader = YoutubeLoader.from_youtube_url(
            youtube_link,
            language=["en", "id"],                      # Supports both English and Indonesian
            translation="en",                           # Translates non-English parts to English
            transcript_format=TranscriptFormat.CHUNKS,  # Load transcript in chunks
            chunk_size_seconds=30                       # Chunk duration set to 30 seconds
        )
        transcript = ""
        for doc in loader.load():
            transcript += doc.page_content
        return transcript
    except Exception as e:
        st.error(f"Error extracting transcript: {str(e)}")
        return None

# Prompt template for generating the summary
prompt = """
    You are a YouTube video summarizer. Given the transcript text, your task is to summarize the key points and main takeaways of the video. 
    The summary should be concise, covering the most important information in bullet points. 
    Your summary should not exceed 250 words.
"""

def model_output(input_text):
    """
    Interacts with the Gemini model to generate a summary based on the provided input.
    """
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + input_text)
    return response.text

st.title("YouTube Video Summarizer")

# Input for YouTube video URL
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    # Extract the video ID from the YouTube link
    video_id = youtube_link.split("=")[-1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True) 

if st.button("Get Detailed Notes"):
    transcript_text = extract_video_transcript(youtube_link)
    
    if transcript_text:
        summary = model_output(transcript_text)
        
        st.markdown("## Detailed Notes:")
        st.write(summary)
    else:
        st.write("Sorry, we couldn't retrieve the transcript.")
