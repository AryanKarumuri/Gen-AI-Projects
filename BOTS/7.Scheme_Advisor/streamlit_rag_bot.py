import os
import asyncio
import fitz
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone

from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain_mongodb.retrievers.hybrid_search import MongoDBAtlasHybridSearchRetriever

from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

import streamlit as st

# Only print this once when the module is loaded
print("📦 All dependencies installed successfully!")

# Set page config
st.set_page_config(
    page_title="MSME Scheme Advisor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #1f77b4, #2ca02c, #d62728);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Subheader styling */
    .subheader {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #31333F;
        margin-bottom: 1rem;
    }
    
    /* Card styling */
    .stCard {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1rem;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 8px;
        height: 3rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Input styling */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #1f77b4;
        box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.2);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1.1rem;
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    /* Scheme name styling */
    .scheme-name {
        color: #1f77b4;
        font-weight: 700;
        font-size: 1.2rem;
    }
    
    /* Answer container */
    .answer-container {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 1.5rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1.5rem;
    }
    
    /* Context container */
    .context-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        max-height: 300px;
        overflow-y: auto;
    }
    
    /* Sidebar styling */
    [data-testid=stSidebar] {
        background-color: #f8f9fa;
    }
    
    /* Progress bar styling */
    .stProgress>div>div {
        background-color: #2ca02c;
    }
    
    /* Custom divider */
    .custom-divider {
        border-top: 2px solid #e0e0e0;
        margin: 1.5rem 0;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        border-radius: 0 4px 4px 0;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configuration Constants
OLLAMA_URL = "https://ollama.com" # Replace with your Ollama server URL if self-hosted
DEFAULT_MODEL = "granite4:tiny-h"
EMBED_MODEL = "snowflake-arctic-embed2:latest"
DATA_DIR = Path("/data")


MONGO_URI = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority" # Replace with your MongoDB Atlas connection string
DB_NAME = "msme" # Replace with your database name
VECTOR_NAMESPACE = f"{DB_NAME}.docs"
VECTOR_INDEX = "vector_index"
FULLTEXT_INDEX = "fulltext_index"  # Atlas search index for BM25
USER_COLLECTION = "users_collection"
MEMORY_COLLECTION = "long_term_memory"
COLLECTION_NAME = "pdf_collection"


@st.cache_resource(show_spinner=False)
def init_db():
    """Initialize MongoDB connection and collections"""
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[DB_NAME]
    pdf_collection = db[COLLECTION_NAME]
    user_col = db[USER_COLLECTION]
    memory_col = db[MEMORY_COLLECTION]
    pdf_collection.create_index([("source", 1), ("chunk", 1)], unique=True)
    return mongo_client, db, pdf_collection, user_col, memory_col


@st.cache_resource(show_spinner=False)
def init_models():
    """Initialize LLM and embedding models"""
    try:
        model = ChatOllama(
            model=DEFAULT_MODEL,
            base_url=OLLAMA_URL,
            temperature=0.2,
            max_tokens=500,
            repeat_penalty=1.1,
            top_k=10,
            top_p=0.95
        )
        embeddings = OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_URL)
        return model, embeddings
    except Exception as e:
        st.error(f"❌ Error initializing models: {e}")
        raise e

@st.cache_resource(show_spinner=False)
def init_vector_store(_embeddings):
    """Initialize vector store with embeddings"""
    try:
        vector_store = MongoDBAtlasVectorSearch.from_connection_string(
            connection_string=MONGO_URI,
            namespace=VECTOR_NAMESPACE,
            embedding=_embeddings,
            index_name=VECTOR_INDEX,
            auto_create_index=True,
            auto_index_timeout=60,
            relevance_score_fn="cosine"
        )
        return vector_store
    except Exception as e:
        st.error(f"❌ Error initializing Vector Store: {e}")
        raise e


@st.cache_resource(show_spinner=False)
def init_retriever(_vector_store):
    """Initialize hybrid search retriever"""
    try:
        hybrid_retriever = MongoDBAtlasHybridSearchRetriever(
            vectorstore=_vector_store,
            search_index_name=FULLTEXT_INDEX,
            top_k=10,
            fulltext_penalty=50.0,
            vector_penalty=50.0
        )
        return hybrid_retriever
    except Exception as e:
        st.error(f"❌ Error initializing Hybrid Retriever: {e}")
        raise e


# === PDF Ingestion to Vector Store ===
def pdf_to_docs(pdf_collection):
    docs = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=[
            "\n\n## ",
            "\n\n# ",
            "\n\n",
            "\n",
            "\n\n**",
            ". ",
            " ",
            ""
        ]
    )
    pdf_files = list(sorted(DATA_DIR.glob("*.pdf")))
    
    if not pdf_files:
        st.info("ℹ️ No PDF files found in the data directory.")
        return docs
        
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, pdf in enumerate(pdf_files):
        # Update progress
        progress = (i + 1) / len(pdf_files)
        progress_bar.progress(progress)
        status_text.caption(f"Processing {i+1}/{len(pdf_files)}: {pdf.name}")
        
        # Skip if already in collection
        existing = pdf_collection.count_documents({"source": pdf.name})
        if existing > 0:
            continue

        try:
            with fitz.open(pdf) as doc:
                text = "\n".join(page.get_text("text") for page in doc)
        except Exception as e:
            st.warning(f"❌ Failed to read {pdf.name}: {e}")
            continue

        chunks = splitter.split_text(text)

        for i, chunk in enumerate(chunks):
            doc_obj = Document(
                page_content=chunk,
                metadata={"source": pdf.name, "chunk": i}
            )

            # Save to MongoDB collection (not vector yet)
            try:
                pdf_collection.insert_one({
                    "source": pdf.name,
                    "chunk": i,
                    "content": chunk
                })
                docs.append(doc_obj)
            except DuplicateKeyError:
                pass  # Skip duplicates

    progress_bar.empty()
    status_text.empty()
    return docs


@st.cache_resource(show_spinner=False)
def init_reranker(_hybrid_retriever):
    """Initialize reranker with hybrid retriever"""
    try:
        reranker_model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
        compressor = CrossEncoderReranker(model=reranker_model, top_n=5)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=_hybrid_retriever
        )
        return compression_retriever
    except Exception as e:
        st.error(f"❌ Error initializing Reranker: {e}")
        raise e


SYSTEM_RECOMMENDER = """
### ROLE & IDENTITY
You are an expert Scheme Eligibility Analyst for MSMEs, NGOs, and Startups. Your function is to analyze retrieved documents (Context) and extract precise information about government and institutional schemes. You must act as a strict bridge between the User's Query and the Provided Context.

### CORE PROTOCOL regarding CONTEXT
1. **Source of Truth:** Your knowledge is **exclusively** limited to the provided text chunks (Context). Do not use outside knowledge, even if you know the scheme from your pre-training.
2. **Silence on Absence:** If the answer is not in the context, do not attempt to answer. State clearly: "There is no mention in the provided context."

---

### OPERATIONAL LOGIC & SCENARIOS

#### SCENARIO 1: User asks for a LIST of available schemes
**Action:** Scan the context and extract scheme names.
**Filtration Rules (Critical):**
* **Identify Entities:** Look for proper nouns and distinct program names (e.g., "PM SVANidhi", "CGTMSE").
* **Purge Artifacts:** Aggressively filter out non-scheme text. Do NOT list:
    * Section headers (e.g., "NEW SCHEMES", "CHAPTER 4").
    * Page numbers or alphanumeric codes (e.g., "MSME Schemes 18").
    * Generic labels (e.g., "Introduction", "Eligibility Criteria").
* **Deduplicate:** Ensure each scheme is listed only once.

**Output Format:**
* **[Scheme Name]**: [One-line summary based *strictly* on context].
*(If no summary exists in text, list only the Name).*

#### SCENARIO 2: User asks for DETAILS of a specific scheme
**Action:** Extract specific attributes (Objective, Benefits, Eligibility).
**Alias Handling:** You may match user abbreviations (e.g., "PMEGP") to full names in the text (e.g., "Prime Minister's Employment Generation Programme") ONLY if the full name appears in the context.

**Output Format:**
* **Scheme Name:** [Full Name]
* **Objective:** [Quote or paraphrase from text]
* **Key Benefits:** [Bullet points from text]

#### SCENARIO 3: User asks for ELIGIBILITY / FIT (Profile Analysis)
**Action:** Compare User Profile Data against Scheme Criteria found in the text.
* **Step 1:** Extract User Data (Turnover, Sector, Registration Type, etc.).
* **Step 2:** Locate Scheme Eligibility Rules in context.
* **Step 3:** Map Data to Rules.

**Output Format:**
* **Scheme:** [Name]
* **Verdict:** [Highly Suitable / Potentially Suitable / Not Suitable / Need More Info]
* **Reasoning:** "Based on your turnover of [User Amount], you qualify because the scheme allows up to [Scheme Limit]."
* *If data is missing:* "To confirm eligibility for [Scheme Name], please provide your [Missing Metric, e.g., Udyam Registration Status]."

---

### NEGATIVE CONSTRAINTS (DO NOT IGNORE)
1. **No Hallucinations:** Never invent benefits, limits, or criteria. If the text says "Loans up to ₹1 Cr", do not say "approx ₹1 Cr". Be exact.
2. **No External Suggestions:** Do not recommend schemes that are not present in the provided snippets, even if they are popular in the real world.
3. **No Ambiguity:** If the context mentions a scheme name but provides zero details about it, state: "The scheme [Name] is mentioned, but the document provides no details regarding its benefits or eligibility."

### EXAMPLE INTERACTION

**Input Context:**
"...Page 14... MSME SCHEMES 2024... The ZED Certification Scheme aims to promote Zero Defect Zero Effect manufacturing. Subsidy: 80% for Micro enterprises. ... CHAPTER 5..."

**User Query:** "List available schemes."

**Correct Response:**
* **ZED Certification Scheme**: Aims to promote Zero Defect Zero Effect manufacturing with subsidies for enterprises.

**(Note: "MSME SCHEMES 2024" and "CHAPTER 5" were correctly ignored.)**
"""


USER_TEMPLATE = """
You must answer ONLY based on the retrieved context provided below.
Do NOT generate or guess any information that is not explicitly present in the context.


Retrieved context:
{context}

Question: {question}
"""

RECOMMENDER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_RECOMMENDER),
    ("user", USER_TEMPLATE)
])


@st.cache_resource(show_spinner=False)
def init_rag_chain(_model):
    """Initialize RAG chain with model"""
    try:
        rag_chain: RunnableSequence = (
            {
                "context": lambda x: x["context"],
                "question": lambda x: x["question"],
            }
            | RECOMMENDER_PROMPT
            | _model
            | StrOutputParser()
        )
        return rag_chain
    except Exception as e:
        st.error(f"❌ Error initializing RAG Chain: {e}")
        raise e

if "initialized" not in st.session_state:
    with st.spinner("Initializing components..."):
        # Database initialization
        mongo_client, db, pdf_collection, user_col, memory_col = init_db()
        
        # Models initialization
        model, embeddings = init_models()
        
        # Vector store initialization
        vector_store = init_vector_store(embeddings)
        
        # Retriever initialization
        hybrid_retriever = init_retriever(vector_store)
        
        # Reranker initialization
        compression_retriever = init_reranker(hybrid_retriever)
        
        # RAG chain initialization
        rag_chain = init_rag_chain(model)
        
        # Store in session state
        st.session_state.update({
            "mongo_client": mongo_client,
            "db": db,
            "pdf_collection": pdf_collection,
            "user_col": user_col,
            "memory_col": memory_col,
            "model": model,
            "embeddings": embeddings,
            "vector_store": vector_store,
            "hybrid_retriever": hybrid_retriever,
            "compression_retriever": compression_retriever,
            "rag_chain": rag_chain,
            "initialized": True
        })

# Retrieve components from session state
if "initialized" in st.session_state:
    pdf_collection = st.session_state.pdf_collection
    compression_retriever = st.session_state.compression_retriever
    rag_chain = st.session_state.rag_chain

# Main header
st.markdown("<h1 class='main-header'>🤖 MSME Scheme Advisor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>Get personalized recommendations for MSME schemes and benefits</p>", unsafe_allow_html=True)

# Create tabs for better organization
tab1, tab2 = st.tabs(["💬 Chat", "📚 Manage Documents"])

with tab1:
    st.markdown("<h2 class='subheader'>Ask About MSME Schemes</h2>", unsafe_allow_html=True)
    
    # Example queries in an expander
    with st.expander("💡 Example queries to try"):
        st.markdown("""
        - What MSME schemes are available for small startups?
        - Tell me about the PM SVANidhi scheme
        - What are the benefits of CGTMSE for a small enterprise?
        - I'm a private limited company with ₹50 lakhs turnover. Which schemes suit me?
        """)
    
    # Query input with better styling
    query = st.text_input("Enter your question:", placeholder="e.g., What schemes are available for small businesses?", label_visibility="collapsed")
    
    if query:
        with st.spinner("🤖 Analyzing schemes and preparing recommendations..."):
            try:
                retrieved_docs = st.session_state.compression_retriever.invoke(query)
                context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
                response = st.session_state.rag_chain.invoke({"question": query, "context": context_text})
                
                # Display answer in a styled container
                st.markdown("<h3>📋 Recommended Schemes</h3>", unsafe_allow_html=True)
                st.markdown(response)
                st.markdown("</div>", unsafe_allow_html=True)

                # Show context in expander with better styling
                with st.expander("🔍 View Retrieved Context"):
                    st.text(context_text)
                    st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error during retrieval or response generation: {e}")

with tab2:
    st.markdown("<h2 class='subheader'>Document Management</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📁 Ingest New Documents")
        if st.button("Ingest New PDFs", type="primary", use_container_width=True):
            with st.spinner("Ingesting new PDFs..."):
                docs = pdf_to_docs(st.session_state.pdf_collection)
                if docs:
                    with st.spinner("Indexing documents..."):
                        st.session_state.vector_store.add_documents(docs)
                    st.success(f"✅ Successfully indexed {len(docs)} PDF chunks!")
                    st.info(f"📄 Processed documents from {len(set(d.metadata['source'] for d in docs))} files")
                else:
                    st.info("ℹ️ No new PDF documents found for indexing.")
    
    with col2:
        st.markdown("#### 📊 System Status")
        # Show some stats if available
        try:
            doc_count = st.session_state.pdf_collection.count_documents({})
            st.metric("Indexed Documents", doc_count)
            st.success("✅ System Ready")
        except:
            st.warning("⚠️ Database connection pending")
    
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    
    st.markdown("#### 📝 How to Add New Documents")
    st.markdown("""
    1. Place your PDF documents in the `../rag/data` folder
    2. Click "Ingest New PDFs" to process them
    3. The system will automatically extract and index the content
    4. Your documents will be available for scheme recommendations
    """)