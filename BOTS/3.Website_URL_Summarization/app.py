import os
import langchain
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.docstore.document import Document
from unstructured.cleaners.core import remove_punctuation, clean, clean_extra_whitespace
from langchain.chains.summarize import load_summarize_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st

load_dotenv()

# Extract page content from URL
def content_extraction(url):
    loader = UnstructuredURLLoader(urls=[url], modes="elements", post_processors=[remove_punctuation, clean, clean_extra_whitespace])
    elements = loader.load()
    content = " ".join([element.page_content for element in elements])

    if not content:
        print("Warning: No relevant content extracted.")
    return content 

# Summarize the content
def summarizer(url): 
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2, api_key=os.getenv("GEMINI_API_KEY"))
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    content = content_extraction(url)
    doc = Document(page_content=content)  
    summary = chain.invoke([doc])  
    #print(summary) #for testing/checking the content
    return summary

# Streamlit UI
st.title('Website URL Summarizer')

# Input URL
url_input = st.text_input("Enter the URL to summarize:")

if url_input:
    st.write("Processing your request...")
    try:
        result = summarizer(url_input)
        st.subheader("Summary:")
        st.write(result['output_text'])
    except Exception as e:
        st.error(f"An error occurred: {e}")


#url = "https://community.intel.com/t5/Blogs/Intel/We-Are-Intel/Get-To-Know-Aryan-Karumuri-Mentor-at-Intel-Liftoff-for-AI/post/1611929"
