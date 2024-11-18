import os
import langchain
import streamlit as st
import google.generativeai as genai
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.youtube import TranscriptFormat


# Configuration and API key for Google Gemini
gemini_api_key = "Your_Api_Key"
genai.configure(api_key=gemini_api_key)

# To extract the video transcript from a YouTube video URL.
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

# To generate a summary based on the provided input using Gemini model.
def model_output(input_text, summary_length):
    if summary_length == "Short":
        prompt = "Summarize the video in 4-5 concise bullet points."
    elif summary_length == "Medium":
        prompt = "Summarize the video in 7-9 bullet points with key details."
    else:
        prompt = "Summarize the video in 10-13 bullet points, including the main insights and details."

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + input_text)
    return response.text
    
st.title("YouTube Video Summarizer")

# Input for YouTube video URL
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("=")[-1]  # Extract video ID from the URL
    
    # Display video thumbnail
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

# Select Summary Length (Short, Medium, Long)
summary_length = st.selectbox("Select Summary Length:", ["Short", "Medium", "Long"])

search_keyword = st.text_input("Search for a keyword in the transcript:")

if st.button("Get Detailed Notes"):
    with st.spinner("Extracting transcript..."):
        transcript_text = extract_video_transcript(youtube_link)
    
    if transcript_text:
        if search_keyword:
            # Filter transcript based on the search keyword
            relevant_sections = [chunk for chunk in transcript_text.split("\n") if search_keyword.lower() in chunk.lower()]
            filtered_text = "\n".join(relevant_sections)
            if filtered_text:
                st.write("Summary for selected keyword(s):")
                summary = model_output(filtered_text, summary_length)
                st.write(summary)
            else:
                st.write("No relevant sections found for the given keyword.")
        else:
            with st.spinner("Generating summary..."):
                summary = model_output(transcript_text, summary_length)
                st.write(summary)
                
    else:
        st.write("Sorry, we couldn't retrieve the transcript.")
