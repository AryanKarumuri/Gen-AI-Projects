import os
import logging
import requests
from typing import Optional
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="VLM File Processor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
SUPPORTED_FORMATS = ['pdf', 'png', 'jpg', 'jpeg']
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen3-vl:235b-instruct-cloud")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def init_session_state():
    """Initialize session state variables."""
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []
    if 'current_output' not in st.session_state:
        st.session_state.current_output = None
    if 'current_filename' not in st.session_state:
        st.session_state.current_filename = None


def get_output_files() -> list:
    """Get list of all generated markdown files from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/output")
        if response.status_code == 200:
            data = response.json()
            return data.get("files", [])
        return []
    except requests.RequestException as e:
        logger.error(f"Error fetching output files: {e}")
        return []


def read_output_file(filename: str) -> str:
    """Read content of a markdown file from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/output/{filename}")
        if response.status_code == 200:
            return response.text
        return ""
    except requests.RequestException as e:
        logger.error(f"Error reading file {filename}: {e}")
        return ""


def delete_output_file(filename: str) -> bool:
    """Delete a markdown file via API."""
    try:
        response = requests.delete(f"{API_BASE_URL}/api/output/{filename}")
        return response.status_code == 200
    except requests.RequestException as e:
        logger.error(f"Error deleting file {filename}: {e}")
        return False


def parse_file_via_api(file, model: str) -> tuple[bool, str, Optional[str]]:
    """Process file via API endpoint."""
    try:
        files = {"file": (file.name, file, file.type)}
        data = {"model": model}
        
        response = requests.post(
            f"{API_BASE_URL}/api/parse-file",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            output_filename = result.get("filename")
            return True, "File processed successfully!", output_filename
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return False, f"Error: {error_detail}", None
            
    except requests.ConnectionError:
        return False, "Cannot connect to API. Make sure the FastAPI server is running.", None
    except requests.RequestException as e:
        return False, f"Request error: {str(e)}", None
    except Exception as e:
        return False, f"Unexpected error: {str(e)}", None


def main():
    """Main Streamlit application."""
    init_session_state()

    # Header
    st.title("📄 VLM File Processor")
    st.markdown("""
    Upload PDF or image files to convert them to structured markdown using Vision Language Models.
    """)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Connection Status
        try:
            response = requests.get(f"{API_BASE_URL}/api/", timeout=2)
            if response.status_code == 200:
                st.success("✅ API Connected")
            else:
                st.warning("⚠️ API Unreachable")
        except requests.RequestException:
            st.error("❌ API Disconnected")
        
        st.markdown(f"**API URL:** `{API_BASE_URL}`")
        st.markdown("---")
        
        # Model selection
        model = st.text_input(
            "Ollama Model",
            value=DEFAULT_MODEL,
            help="Name of the model used for processing"
        )

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📤 Upload File")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=SUPPORTED_FORMATS,
            help=f"Upload a PDF or image file ({', '.join(SUPPORTED_FORMATS)}). Make sure the file size is under {MAX_FILE_SIZE // (1024*1024)} MB."
        )

        if uploaded_file is not None:
            # Display file info
            file_size = uploaded_file.size
            file_ext = uploaded_file.name.split('.')[-1].lower()
            
            st.info(f"""
            **File Name:** {uploaded_file.name}  
            **File Size:** {file_size / (1024*1024):.2f} MB  
            **File Type:** {file_ext.upper()}
            """)

            # Validate file size
            if file_size > MAX_FILE_SIZE:
                st.error(f"❌ File size exceeds the maximum limit of {MAX_FILE_SIZE // (1024*1024)} MB")
                return

            # Process button
            if st.button("🚀 Process File", type="primary", use_container_width=True):
                with st.spinner("Processing file... This may take a while."):
                    success, message, output_filename = parse_file_via_api(uploaded_file, model)
                    
                    if success and output_filename:
                        # Update session state
                        st.session_state.current_output = read_output_file(output_filename)
                        st.session_state.current_filename = output_filename
                        st.session_state.processed_files = get_output_files()
                        
                        st.success(f"✅ {message} Output saved as `{output_filename}`")
                    else:
                        st.error(f"❌ {message}")

    with col2:
        st.header("📋 Output")

        # Display current output
        if st.session_state.current_output:
            st.markdown(f"**Current File:** `{st.session_state.current_filename}`")
            st.markdown("---")
            
            # Display markdown content
            st.markdown(st.session_state.current_output)
            
            # Download button
            st.download_button(
                label="📥 Download Markdown",
                data=st.session_state.current_output,
                file_name=st.session_state.current_filename,
                mime="text/markdown",
                use_container_width=True
            )
        else:
            st.info("👆 Upload and process a file to see the output here.")

    # Previous outputs section
    st.markdown("---")
    st.header("📁 Previous Outputs")

    # Refresh button
    if st.button("🔄 Refresh File List"):
        st.session_state.processed_files = get_output_files()
        st.rerun()

    # Display file list
    output_files = get_output_files()
    
    if output_files:
        st.info(f"Found **{len(output_files)}** processed file(s)")
        
        for filename in output_files:
            with st.expander(f"📄 {filename}", expanded=False):
                col_a, col_b, col_c = st.columns([3, 1, 1])
                
                with col_a:
                    st.markdown(f"**File:** `{filename}`")
                
                with col_b:
                    if st.button(f"👁️ View", key=f"view_{filename}"):
                        st.session_state.current_output = read_output_file(filename)
                        st.session_state.current_filename = filename
                        st.rerun()
                
                with col_c:
                    if st.button(f"🗑️ Delete", key=f"delete_{filename}"):
                        if delete_output_file(filename):
                            st.success(f"Deleted `{filename}`")
                            st.session_state.processed_files = get_output_files()
                            if st.session_state.current_filename == filename:
                                st.session_state.current_output = None
                                st.session_state.current_filename = None
                            st.rerun()
                        else:
                            st.error(f"Failed to delete `{filename}`")
    else:
        st.info("No processed files found. Upload a file to get started!")

if __name__ == "__main__":
    main()