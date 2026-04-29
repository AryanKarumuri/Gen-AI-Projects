import streamlit as st
import tiktoken
from transformers import AutoTokenizer
import io

st.set_page_config(page_title="Token Counter", page_icon="🧮", layout="wide")

st.title("🔢 Token Counter")
st.markdown("Count tokens across multiple popular tokenizers. Supports text input and file uploads.")

# --- Tokenizer Registry ---
TOKENIZERS = {
    "OpenAI GPT-4 / GPT-4o (cl100k_base)": "cl100k_base",
    "OpenAI GPT-4o (o200k_base)": "o200k_base",
    "OpenAI GPT-3.5 / text-embedding-ada-002 (cl100k_base)": "cl100k_base",
    "OpenAI GPT-3 / p50k_base": "p50k_base",
    "OpenAI r50k_base": "r50k_base",
    "Hugging Face GPT-2": "gpt2",
    "Hugging Face Meta-Llama-3-8B": "meta-llama/Meta-Llama-3-8B",
    "Hugging Face Mistral-7B": "mistralai/Mistral-7B-v0.1",
    "Hugging Face google/gemma-2b": "google/gemma-2b",
    "Hugging Face microsoft/Phi-3-mini-4k-instruct": "microsoft/Phi-3-mini-4k-instruct",
}

@st.cache_resource(show_spinner=False)
def load_hf_tokenizer(name):
    return AutoTokenizer.from_pretrained(name, trust_remote_code=True)

def count_tokens(text, tokenizer_name):
    if tokenizer_name.startswith("cl100k_base") or tokenizer_name.startswith("o200k_base") or tokenizer_name.startswith("p50k_base") or tokenizer_name.startswith("r50k_base"):
        enc = tiktoken.get_encoding(tokenizer_name)
        return len(enc.encode(text))
    else:
        tokenizer = load_hf_tokenizer(tokenizer_name)
        return len(tokenizer.encode(text, add_special_tokens=False))

# --- Sidebar ---
st.sidebar.header("⚙️ Settings")
selected_models = st.sidebar.multiselect(
    "Select tokenizers to compare",
    options=list(TOKENIZERS.keys()),
    default=["OpenAI GPT-4o (o200k_base)", "OpenAI GPT-4 / GPT-4o (cl100k_base)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Tips")
st.sidebar.markdown("- **o200k_base** is the latest OpenAI tokenizer (GPT-4o).")
st.sidebar.markdown("- **cl100k_base** is used by GPT-4 and GPT-3.5.")
st.sidebar.markdown("- Hugging Face tokenizers are downloaded on first use.")

# --- Input Section ---
tab1, tab2 = st.tabs(["📝 Text Input", "📁 File Upload"])

text = ""

with tab1:
    text = st.text_area("Paste your prompt/text here:", height=300, placeholder="Enter your text here...")

with tab2:
    uploaded_file = st.file_uploader("Upload a file", type=["txt", "md", "py", "json", "csv", "html", "xml", "yaml", "yml", "js", "ts", "css", "java", "c", "cpp", "cs", "go", "rs", "php", "swift", "kt", "r", "sql", "sh", "bat", "ps1", "ini", "cfg", "log"])
    if uploaded_file is not None:
        try:
            text = uploaded_file.read().decode("utf-8")
            st.success(f"Loaded `{uploaded_file.name}` ({len(text):,} characters)")
            with st.expander("Preview"):
                st.code(text[:2000] + ("..." if len(text) > 2000 else ""), language="text")
        except Exception as e:
            st.error(f"Could not read file: {e}")

# --- Results ---
if text.strip():
    st.markdown("---")
    st.subheader("📊 Results")

    char_count = len(text)
    word_count = len(text.split())
    line_count = text.count("\n") + 1
    tiktoken_count = len(tiktoken.get_encoding("o200k_base").encode(text))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Characters", f"{char_count:,}")
    col2.metric("Words", f"{word_count:,}")
    col3.metric("Lines", f"{line_count:,}")
    col4.metric("Tokens (tiktoken)", f"{tiktoken_count:,}")

    if selected_models:
        st.markdown("#### Token Counts by Model")
        results = []
        with st.status("🔄 Counting tokens...", expanded=False) as status:
            for model_name in selected_models:
                tokenizer_key = TOKENIZERS[model_name]
                try:
                    token_count = count_tokens(text, tokenizer_key)
                    results.append({"Model / Tokenizer": model_name, "Tokens": token_count})
                except Exception as e:
                    results.append({"Model / Tokenizer": model_name, "Tokens": f"Error: {e}"})
            status.update(label="✅ Done!", state="complete")

        st.dataframe(results, width='stretch', hide_index=True)

        # Highlight best / most common
        numeric_results = [r for r in results if isinstance(r["Tokens"], int)]
        if numeric_results:
            max_tokens = max(numeric_results, key=lambda x: x["Tokens"])
            min_tokens = min(numeric_results, key=lambda x: x["Tokens"])
            st.caption(f"🔺 Highest: **{max_tokens['Model / Tokenizer']}** ({max_tokens['Tokens']:,} tokens)  |  🔻 Lowest: **{min_tokens['Model / Tokenizer']}** ({min_tokens['Tokens']:,} tokens)")
    else:
        st.info("Select at least one tokenizer from the sidebar to see token counts.")
else:
    st.info("Enter some text or upload a file to get started.")
