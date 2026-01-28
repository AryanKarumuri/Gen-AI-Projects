import os
import io
import fitz
import logging
from ollama import Client
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = ['pdf', 'png', 'jpg', 'jpeg']

SYSTEM_PROMPT = """You are an expert document parser specializing in converting PDF pages to clean, semantic markdown.

**Your Task:**
Extract content from the provided page image and return it as high-quality markdown. Prioritize semantic meaning and readability over rigid pixel-perfect layout preservation.

**1. Text Extraction & Cleaning:**
- **OCR Correction:** Correct obvious OCR artifacts (e.g., "fi1e" → "file", "rn" → "m") but preserve genuine author spelling/grammar errors.
- **Reading Order:** Follow logical reading order (typically top-to-bottom, left-to-right).
- **Multi-Column:** Process the left column completely before moving to the right column.
- **Structure:** Use headers (`#`, `##`, `###`) to reflect the document's semantic hierarchy, not just font size.
- **Exclusions:** IGNORE running headers, footers, page numbers, and repeated watermarks unless they contain unique information vital to the text.

**2. Handling Layouts & Elements:**
- **Lists:** Use proper markdown syntax for bullets (`-`) and numbered lists (`1.`).
- **Emphasis:** Preserve **bold**, *italics*, and `code` formatting.
- **Sidebars/Callouts:** If a distinct sidebar or note box appears, insert it as a blockquote (`>`) immediately following the paragraph it relates to.
- **Links:** Extract visible URLs as `[text](url)`.

**3. Tables (Strict Logic):**
- **Simple Tables:** Convert to standard markdown tables.
- **Complex Tables:** If a table uses merged cells (rowspan/colspan) or complex nesting that markdown cannot support:
  - Option A: Use HTML `<table>` syntax if precision is critical.
  - Option B: Flatten the data into a structured bulleted list if HTML is not allowed.
- *Preserve the integrity of the data above all else.*

**4. Mathematical Formulas:**
- Use standard LaTeX syntax.
- Inline math: `$ ... $`
- Display math (standalone equations): `$$...$$`
- Ensure symbols are correctly transcribed (e.g., superscripts, subscripts, Greek letters).

**5. Visuals (Images, Charts, Diagrams):**
- Insert markdown image placeholder: `![Description](image)`
- Immediately follow with a descriptive block labeled **"Visual Description:"** containing:
  * Type of visual (photo, diagram, chart, graph, illustration)
  * Main subject or purpose
  * Key elements, labels, or data points
  * Colors, patterns, or notable visual features
  * Context or relationship to surrounding text
- For charts/graphs: Describe axes labels, data series, trends, key data points, and any legends
- For diagrams: Explain components, connections, flows, and relationships between elements
- For technical figures: Include measurements, specifications, or quantitative data when visible

**Special Elements:**
- Footnotes: Use markdown footnote syntax `[^1]`
- Citations: Preserve as written
- Code blocks: Use triple backticks with language specification
- Quotes: Use `>` for blockquotes
- Links: Preserve as `[text](url)` if visible

**Quality Guidelines:**
- DO NOT add explanations, comments, or meta-information
- DO NOT truncate or summarize.
- DO NOT invent or hallucinate text not present in the image
- DO NOT include "Here is the markdown..." or similar preambles
- Output ONLY the markdown content, nothing else

**Output Format:**
Return raw markdown with no wrapper, no code blocks, no explanations.
Start immediately with the page content.
""".strip()

def init_ollama():
    base_url = os.getenv("OLLAMA_BASE_URL")
    api_key = os.getenv("OLLAMA_API_KEY")
    try:
        ollama_client = Client(
            host=base_url,
            headers={'Authorization': f'Bearer {api_key}'} if api_key else {}
        )
        logging.info("Ollama client initialized successfully.")
        return ollama_client
    except Exception as e:
        logging.error(f"Failed to initialize Ollama client: {e}")
        raise

def parse_file(file_path: str, model: str = None, original_filename: str = "") -> list[str]:
    if model is None:
        model = os.getenv("DEFAULT_MODEL", "qwen3-vl:235b-instruct-cloud")
    ollama_client = init_ollama()

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()[1:]  # Remove the dot and convert to lower case

    if ext == 'pdf':
        # Handle PDF files
        try:
            pdf_doc = fitz.open(file_path)
        except Exception as e:
            logger.error(f"Failed to open PDF file: {file_path} - {e}")
            raise ValueError(f"Cannot open PDF file: {file_path}") from e
        
        markdown_pages = []
        
        try:
            for page_num in range(pdf_doc.page_count):
                try:
                    logger.info(f"Processing page {page_num + 1}/{pdf_doc.page_count}")
                    page = pdf_doc[page_num]

                    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3)) 
                    img_data = pix.tobytes("png")

                    response = ollama_client.chat(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": SYSTEM_PROMPT,
                            },
                            {
                                "role": "user",
                                "content": (
                                    "Convert this page to Markdown.\n\n"
                                    "IMPORTANT: Look carefully for any **graphs, charts, or diagrams**.\n"
                                    "If found, you MUST provide a detailed 'Visual Description' block explaining the data/structure.\n"
                                    "Do not ignore the visual elements."
                                ),
                                "images": [img_data],
                            },
                        ]
                    )

                    content = response["message"]["content"]
                    markdown_pages.append(content)
                    logger.info(f"Completed page {page_num + 1}")

                except Exception as e:
                    logger.error(f"Error processing page {page_num + 1}: {e}")
                    raise ValueError(f"Failed to process page {page_num + 1}: {str(e)}") from e
        finally:
            pdf_doc.close()
        
        return markdown_pages
    elif ext in ['png', 'jpg', 'jpeg']:
        try:
            with open(file_path, "rb") as img_file:
                img_data = img_file.read()
            
            logger.info(f"Processing image: {file_path}")
            
            response = ollama_client.chat(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": (
                            "Convert this image to Markdown.\n\n"
                            "IMPORTANT: Look carefully for any **graphs, charts, or diagrams**.\n"
                            "If found, you MUST provide a detailed 'Visual Description' block explaining the data/structure.\n"
                            "Do not ignore the visual elements."
                        ),
                        "images": [img_data],
                    },
                ]
            )

            content = response["message"]["content"]
            logger.info(f"Completed processing image: {file_path}")
            return [content]
            
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {e}")
            raise ValueError(f"Failed to process image {file_path}: {str(e)}") from e
    else:
        raise ValueError(f"Unsupported file format: {ext}")
    
