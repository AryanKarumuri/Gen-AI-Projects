import streamlit as st
import validators
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader, UnstructuredURLLoader

st.set_page_config(page_title="Summarize the Text From YT or Website Seamlessly", page_icon="📄✨")
st.title("Summarize the Text From YT🎥 or Website🌐 Seamlessly")
st.subheader("Summarize URL")

# Provide Groq API key     
with st.sidebar:
    groq_api_key = st.text_input("Groq API Key🔑", value="", type="password")

# URL input
url = st.text_input("URL", label_visibility="collapsed")

# Initialize the LLM only if the API key is provided
if groq_api_key:
    llm = ChatGroq(model="Gemma-7b-It", groq_api_key=groq_api_key)

    # Prompt Template
    prompt_template = PromptTemplate(
        template=(
            "Please provide a clear and concise summary of the following content. "
            "Understand the content and think twice while summarizing the content. "
            "Focus on the main ideas, key details, and overall message. "
            "Content: {text}"
        ),
        input_variables=["text"]
    )

    if st.button("Summarize"):
        if not url.strip():
            st.error("Please provide a URL to get started")
        elif not validators.url(url):
            st.error("Please enter a valid URL. It can be a YT video URL or website URL.")
        else:
            try:
                with st.spinner("Waiting..."):
                    if "youtube.com" in url:
                        try:
                            loader = YoutubeLoader.from_youtube_url(url, add_video_info=True)
                        except Exception as e:
                            st.error(f"Error loading YouTube video: {e}")
                            st.stop()  # Exit the button callback
                    else:
                        loader = UnstructuredURLLoader(urls=[url], ssl_verify=False,
                                                        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"})
                    
                    docs = loader.load()

                    # Chain for summarization
                    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt_template)
                    output_summary = chain.run(input_documents=docs)

                    #input_data = {"input_documents": docs}

                    #output_summary = chain.invoke(input_data)
                    # Displaying the output
                    st.success(output_summary)
            except Exception as e:
                st.exception(f"Exception: {e}")
else:
    st.warning("Please enter your Groq API key.")
