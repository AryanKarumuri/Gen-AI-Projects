import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
import os

# Page configuration
st.set_page_config(
    page_title="Image Generation API",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        height: 3rem;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Initialize session state
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None
if 'last_prompt' not in st.session_state:
    st.session_state.last_prompt = ""

def generate_image(prompt, token, width, height, model, response_format="file"):
    """Generate image using the API."""
    try:
        headers = {
            "X-HuggingFace-Token": token,
            "Content-Type": "application/json"
        }
        
        data = {
            "text": prompt,
            "width": width,
            "height": height,
            "model": model
        }
        
        if response_format == "file":
            endpoint = f"{API_BASE_URL}/api/generate-image"
            response = requests.post(endpoint, headers=headers, json=data)
            
            if response.status_code == 200:
                return Image.open(BytesIO(response.content)), None
            else:
                return None, response.json()
        else:
            endpoint = f"{API_BASE_URL}/api/generate-image-json"
            response = requests.post(endpoint, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                image_data = base64.b64decode(result["image"])
                return Image.open(BytesIO(image_data)), None
            else:
                return None, response.json()
                
    except requests.exceptions.ConnectionError:
        return None, {"detail": "Cannot connect to API. Make sure the server is running."}
    except Exception as e:
        return None, {"detail": str(e)}

# Main App
st.markdown('<h1 class="main-header">🎨 AI Image Generator</h1>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Token
    st.subheader("🔑 API Token")
    hf_token = st.text_input(
        "Hugging Face Token",
        type="password",
        placeholder="Enter your HF token",
        help="Get your token from https://huggingface.co/settings/tokens"
    )
    
    st.divider()
    
    # Image Parameters
    st.subheader("📐 Image Parameters")
    
    # Model Selection
    model_options = [
        "black-forest-labs/FLUX.1-schnell",
        "black-forest-labs/FLUX.1-dev",
        "stabilityai/stable-diffusion-3-medium-diffusers",
        "stabilityai/stable-diffusion-xl-base-1.0"
    ]
    selected_model = st.selectbox(
        "Model",
        model_options,
        index=0,
        help="Choose the AI model for image generation"
    )
    
    # Dimensions
    col1, col2 = st.columns(2)
    with col1:
        width = st.slider(
            "Width",
            min_value=64,
            max_value=2048,
            value=512,
            step=64,
            help="Image width in pixels"
        )
    with col2:
        height = st.slider(
            "Height",
            min_value=64,
            max_value=2048,
            value=512,
            step=64,
            help="Image height in pixels"
        )
    
    st.divider()
    
    # Response Format
    st.subheader("📤 Response Format")
    response_format = st.radio(
        "Choose output format",
        ["File", "JSON (Base64)"],
        help="File: Direct download | JSON: Base64 encoded"
    )
    
    st.divider()
    
    # API Status
    st.subheader("🔌 API Status")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ API is running")
        else:
            st.error("❌ API error")
    except:
        st.error("❌ API not reachable")
        st.info("Make sure to run: uvicorn app.main:app --reload")

# Main Content Area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Prompt")
    
    # Text Input
    prompt = st.text_area(
        "Enter your image description",
        placeholder="A beautiful sunset over mountains with vibrant colors...",
        height=150,
        help="Describe the image you want to generate in detail"
    )
    
    # Example Prompts
    with st.expander("💡 Example Prompts"):
        examples = [
            "A futuristic cityscape at sunset with flying cars",
            "A cute robot painting a canvas in a colorful studio",
            "A majestic dragon flying over a medieval castle",
            "A cozy coffee shop on a rainy day with warm lighting"
        ]
        for example in examples:
            if st.button(example, key=f"example_{examples.index(example)}"):
                prompt = example
    
    # Generate Button
    st.divider()
    generate_btn = st.button(
        "🚀 Generate Image",
        type="primary",
        use_container_width=True,
        disabled=not prompt or not hf_token
    )

with col2:
    st.header("🖼️ Generated Image")
    
    # Image Display Area
    if st.session_state.generated_image:
        st.image(st.session_state.generated_image, use_container_width=True)
        
        # Download Button
        img_buffer = BytesIO()
        st.session_state.generated_image.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        
        st.download_button(
            label="⬇️ Download Image",
            data=img_buffer,
            file_name=f"generated_image_{st.session_state.last_prompt[:20].replace(' ', '_')}.png",
            mime="image/png",
            use_container_width=True
        )
    else:
        st.info("👈 Enter a prompt and click Generate to create an image")

# Handle Generation
if generate_btn and prompt and hf_token:
    with st.spinner("🎨 Generating your image... This may take a moment..."):
        image, error = generate_image(prompt, hf_token, width, height, selected_model, response_format.lower())
        
        if image:
            st.session_state.generated_image = image
            st.session_state.last_prompt = prompt
            st.success("✅ Image generated successfully!")
            st.rerun()
        else:
            st.session_state.generated_image = None
            st.error(f"❌ Error: {error.get('detail', 'Unknown error')}")
            if 'detail' in error and isinstance(error['detail'], list):
                for err in error['detail']:
                    st.error(f"• {err.get('msg', err)}")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Created by Aryan | Built with FastAPI & Streamlit</p>
</div>
""", unsafe_allow_html=True)